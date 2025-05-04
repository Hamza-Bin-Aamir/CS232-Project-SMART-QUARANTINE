import os
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import psycopg2
from dotenv import load_dotenv
import re
import secrets
import json
import datetime
from datetime import time

load_dotenv(os.getcwd() + "\\credentials.env")

def serialize_time(t):
    if t is None:
        return None
    if isinstance(t, time):
        return t.isoformat()  # 'HH:MM:SS' string
    return str(t)

app = Flask("database_server")
app.config['SECRET_KEY'] = secrets.token_hex(16)

def ParseFile(file_loc, data_dictionary) -> str:
    with open(file_loc, 'r') as f:
        sql_content = f.read()

    # Replace placeholders with actual values
    for key, value in data_dictionary.items():
        if isinstance(value, list):
            # Convert list to SQL array format
            formatted_value = ', '.join(map(str, value))
            sql_content = sql_content.replace(f"{{{{{key}}}}}", formatted_value)
        else:
            # Replace single values
            sql_content = sql_content.replace(f"{{{{{key}}}}}", str(value))

    return sql_content

def get_db_connection():
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USERNAME'),
        password=os.getenv('DB_PASSWORD')
    )
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/addpandemic', methods=['GET', 'POST'])
def add_pandemic():
    if request.method == 'GET':
        # Show the form template
        return render_template('add_pandemic.html')
    
    elif request.method == 'POST':
        try:
            # Get form data (works with both JSON and form-data)
            form_data = {
                "PANDEMIC_NAME": request.form.get('pandemic_name'),
                "DATE_START": request.form.get('date_start'),
                "DESCRIPTION": request.form.get('description')
            }
            
            # Validate required fields
            if not form_data["PANDEMIC_NAME"] or not form_data["DATE_START"]:
                flash('Pandemic name and start date are required!', 'error')
                return redirect(url_for('add_pandemic'))
            
            # Generate and execute SQL
            sql_path = os.path.join(os.getcwd(), "SQL", "Insertion", "NewPandemic.SQL")
            generated_sql = ParseFile(sql_path, form_data)
            
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(generated_sql)
            conn.commit()
            cur.close()
            conn.close()
            
            flash('Pandemic added successfully!', 'success')
            return redirect(url_for('add_pandemic'))
        
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
            return redirect(url_for('add_pandemic'))
        
@app.route('/querytool', methods=['GET', 'POST'])
def query_tool():
    if request.method == 'GET':
        # Render a simple form to enter SQL queries
        return render_template('querytool.html')

    elif request.method == 'POST':
        sql_query = request.form.get('sql_query')
        if not sql_query:
            return jsonify({"error": "No SQL query provided"}), 400

        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(sql_query)

            # Try to fetch results if it's a SELECT query
            if cur.description:
                columns = [desc[0] for desc in cur.description]
                rows = cur.fetchall()
                results = [dict(zip(columns, row)) for row in rows]
                cur.close()
                conn.close()
                return jsonify({"results": results})
            else:
                # For INSERT/UPDATE/DELETE queries
                conn.commit()
                cur.close()
                conn.close()
                return jsonify({"message": "Query executed successfully"})
        except Exception as e:
            return jsonify({"error": str(e)}), 400

@app.route('/pandemic-spread', methods=['GET'])
def pandemic_spread():
    conn = get_db_connection()
    cur = conn.cursor()

    # Get list of pandemics for dropdown
    cur.execute("SELECT id, p_name FROM pandemics ORDER BY p_name;")
    pandemics = cur.fetchall()

    # Get query params for selected pandemic and parameter
    pandemic_id = request.args.get('pandemic_id', type=int)
    parameter = request.args.get('parameter', default='infected', type=str)
    valid_params = {'deaths', 'cured', 'infected', 'total_population'}
    if parameter not in valid_params:
        parameter = 'infected'

    # If no pandemic selected, just render page with dropdowns
    if not pandemic_id:
        cur.close()
        conn.close()
        return render_template('pandemic_spread.html', pandemics=pandemics, selected_pandemic=None, parameter=parameter)

    # Query to get latest stats per area for the selected pandemic
    # We assume latest date per area for the pandemic
    cur.execute(f"""
        WITH latest_stats AS (
            SELECT DISTINCT ON (area_id) area_id, {parameter}, stat_date
            FROM pandemic_stats
            WHERE pandemic_id = %s
            ORDER BY area_id, stat_date DESC
        )
        SELECT a.id, a.name, ls.{parameter}
        FROM areas a
        LEFT JOIN latest_stats ls ON a.id = ls.area_id;
    """, (pandemic_id,))
    nodes_data = cur.fetchall()

    # Query adjacency edges with adj_power between areas
    cur.execute("""
        SELECT src, dest, adj_power
        FROM area_adj;
    """)
    edges_data = cur.fetchall()

    cur.close()
    conn.close()

    # Prepare JSON data for D3.js
    nodes = []
    for node_id, name, value in nodes_data:
        nodes.append({
            "id": node_id,
            "name": name,
            "value": value if value is not None else 0
        })

    links = []
    for src, dest, adj_power in edges_data:
        links.append({
            "source": src,
            "target": dest,
            "weight": float(adj_power)
        })

    return render_template('pandemic_spread.html',
                           pandemics=pandemics,
                           selected_pandemic=pandemic_id,
                           parameter=parameter,
                           graph_data=json.dumps({"nodes": nodes, "links": links}))

@app.route('/policy-suggestion', methods=['GET'])
def policy_suggestion():
    conn = get_db_connection()
    cur = conn.cursor()

    # Fetch all areas with their economic makeup info
    areas_query = ParseFile("SQL/Selections/GetAreasWithEconomicMakeup.SQL", {})
    cur.execute(areas_query)
    areas = cur.fetchall()

    # Fetch existing policies with pandemic and type info
    policies_query = ParseFile("SQL/Selections/GetPoliciesWithDetails.SQL", {})
    cur.execute(policies_query)
    policies_raw = cur.fetchall()

    policies = []
    for p in policies_raw:
        policy_id, p_name, pandemic_id, e_zone, t_start, t_end = p
        policies.append((policy_id, p_name, pandemic_id, e_zone, serialize_time(t_start), serialize_time(t_end)))

    # Fetch pandemics for dropdown
    pandemics_query = ParseFile("SQL/Selections/GetPandemics.SQL", {})
    cur.execute(pandemics_query)
    pandemics = cur.fetchall()

    # Fetch economic zones for dropdown
    economic_zones_query = ParseFile("SQL/Selections/GetEconomicZones.SQL", {})
    cur.execute(economic_zones_query)
    economic_zones = cur.fetchall()

    # Fetch suggested policies for each area
    suggested_policies = {}
    for area in areas:
        area_id = area[0]
        economic_zones_ids = [zone for zone in area[2::2] if zone is not None]  # Extract non-null zones
        suggested_policies_query = ParseFile("SQL/Selections/GetSuggestedPolicies.SQL", {
            "ECONOMIC_ZONES_IDS": economic_zones_ids
        })
        cur.execute(suggested_policies_query)
        suggested_policies[area_id] = cur.fetchall()

    cur.close()
    conn.close()

    return render_template('policy_suggestion.html',
                           areas=areas,
                           policies=policies,
                           pandemics=pandemics,
                           economic_zones=economic_zones,
                           suggested_policies=suggested_policies)

# API to create a new policy
@app.route('/api/policy/create', methods=['POST'])
def create_policy():
    data = request.json
    pandemic_id = data.get('pandemic_id')
    p_name = data.get('policy_name')
    economic_zone = data.get('economic_zone')
    time_frame_start = data.get('time_frame_start')
    time_frame_end = data.get('time_frame_end')

    if not (pandemic_id and p_name and economic_zone):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Insert into policy_type table
        cur.execute("""
            INSERT INTO policy_type (e_zone, time_frame_start, time_frame_end)
            VALUES (%s, %s, %s) RETURNING p_type;
        """, (economic_zone, time_frame_start, time_frame_end))
        policy_type_id = cur.fetchone()[0]

        # Insert into policies table
        cur.execute("""
            INSERT INTO policies (pandemic_id, p_name, p_type)
            VALUES (%s, %s, %s) RETURNING policy_id;
        """, (pandemic_id, p_name, policy_type_id))
        policy_id = cur.fetchone()[0]

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"message": "Policy created successfully", "policy_id": policy_id})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# API to implement a policy in an area (add policy_history)
@app.route('/api/policy/implement', methods=['POST'])
def implement_policy():
    data = request.json
    policy_id = data.get('policy_id')
    affected_area = data.get('affected_area')
    date_start = data.get('date_start')

    if not (policy_id and affected_area and date_start):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO policy_history (policy_id, affected_area, date_start)
            VALUES (%s, %s, %s);
        """, (policy_id, affected_area, date_start))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"message": "Policy implemented in area"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# API to modify policy history (change start/end dates)
@app.route('/api/policy/history/update', methods=['POST'])
def update_policy_history():
    data = request.json
    policy_id = data.get('policy_id')
    affected_area = data.get('affected_area')
    date_start = data.get('date_start')
    date_end = data.get('date_end')

    if not (policy_id and affected_area):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            UPDATE policy_history
            SET date_start = %s, date_end = %s
            WHERE policy_id = %s AND affected_area = %s;
        """, (date_start, date_end, policy_id, affected_area))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"message": "Policy history updated"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# API to end a policy (set date_end to today or given date)
@app.route('/api/policy/end', methods=['POST'])
def end_policy():
    data = request.json
    policy_id = data.get('policy_id')
    affected_area = data.get('affected_area')
    date_end = data.get('date_end')

    if not (policy_id and affected_area and date_end):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            UPDATE policy_history
            SET date_end = %s
            WHERE policy_id = %s AND affected_area = %s;
        """, (date_end, policy_id, affected_area))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"message": "Policy ended"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/policy-review', methods=['GET'])
def policy_review():
    conn = get_db_connection()
    cur = conn.cursor()

    # Fetch policy history with pandemic stats
    policy_history_query = ParseFile("SQL/Selections/GetPolicyHistoryWithStats.SQL", {})
    cur.execute(policy_history_query)
    policy_data = cur.fetchall()

    # Calculate effectiveness (example: higher cure rate and lower infection/death rates are better)
    policies = []
    for row in policy_data:
        policy_id, policy_name, pandemic_id, area_name, infection_rate, cure_rate, death_rate, date_start, date_end = row
        effectiveness = (cure_rate - infection_rate - death_rate) * 100  # Example formula
        policies.append({
            "policy_id": policy_id,
            "policy_name": policy_name,
            "pandemic_id": pandemic_id,
            "area_name": area_name,
            "infection_rate": infection_rate,
            "cure_rate": cure_rate,
            "death_rate": death_rate,
            "date_start": date_start,
            "date_end": date_end,
            "effectiveness": round(effectiveness, 2)
        })

    cur.close()
    conn.close()

    return render_template('policy_review.html', policies=policies)

@app.route('/next-day', methods=['GET', 'POST'])
def next_day():
    if request.method == 'GET':
        # Serve the HTML file for the next day simulation
        return render_template('next_day.html')

    elif request.method == 'POST':
        try:
            conn = get_db_connection()
            cur = conn.cursor()

            # Fetch current pandemic stats
            cur.execute("""
                SELECT id, pandemic_id, area_id, total_population, infected, infection_rate, cured, cure_rate, deaths, death_rate
                FROM pandemic_stats;
            """)
            stats = cur.fetchall()

            # Simulate the next day's stats
            updated_stats = []
            for stat in stats:
                stat_id, pandemic_id, area_id, total_population, infected, infection_rate, cured, cure_rate, deaths, death_rate = stat

                # Calculate new infections, recoveries, and deaths
                new_infections = int(infected * infection_rate)
                new_cured = int(infected * cure_rate)
                new_deaths = int(infected * death_rate)

                # Update totals
                infected = max(0, infected + new_infections - new_cured - new_deaths)
                cured += new_cured
                deaths += new_deaths

                # Append updated stats
                updated_stats.append((infected, cured, deaths, stat_id))

            # Update the database with the new stats
            cur.executemany("""
                UPDATE pandemic_stats
                SET infected = %s, cured = %s, deaths = %s
                WHERE id = %s;
            """, updated_stats)

            conn.commit()
            cur.close()
            conn.close()

            return jsonify({"message": "Next day's conditions simulated successfully", "updated_stats": updated_stats})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

app.run(host="0.0.0.0", debug=True)