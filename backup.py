# from flask import Flask, jsonify
# from flask_sqlalchemy import SQLAlchemy
# from flask_cors import CORS
# from flask import request

# import pandas as pd

# app = Flask(__name__)
# CORS(app)

# # Configure the SQLAlchemy part of the application instance
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///insurance.db'  # You can replace this with your database URL
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# # Create the SQLAlchemy db instance
# db = SQLAlchemy(app)

# # Define a model for the data
# class Claim(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     g_loss = db.Column(db.String(100))
#     stage_name = db.Column(db.String(100))
#     stage_seq = db.Column(db.Integer)
#     stage_date = db.Column(db.String(50))
#     t_clm_nbr = db.Column(db.String(100))
#     c_lob = db.Column(db.String(100))
#     c_lob_ctgry = db.Column(db.String(100))
#     market_segment = db.Column(db.String(100))
#     input_method = db.Column(db.String(100))
#     aim_office = db.Column(db.String(100))
#     claim_owner = db.Column(db.String(100))
#     claim_supervisor = db.Column(db.String(100))

#     def __init__(self, g_loss, stage_name, stage_seq, stage_date, t_clm_nbr, c_lob, c_lob_ctgry, market_segment, input_method, aim_office, claim_owner, claim_supervisor):
#         self.g_loss = g_loss
#         self.stage_name = stage_name
#         self.stage_seq = stage_seq
#         self.stage_date = stage_date
#         self.t_clm_nbr = t_clm_nbr
#         self.c_lob = c_lob
#         self.c_lob_ctgry = c_lob_ctgry
#         self.market_segment = market_segment
#         self.input_method = input_method
#         self.aim_office = aim_office
#         self.claim_owner = claim_owner
#         self.claim_supervisor = claim_supervisor

# # Function to load CSV data into the database
# def load_csv_to_db():
#     try:
#         df = pd.read_csv('./data.csv')

#         # Clear existing data in the table
#         db.session.query(Claim).delete()

#         # Insert each row into the database
#         for _, row in df.iterrows():
#             claim = Claim(
#                 g_loss=row['G_LOSS'],
#                 stage_name=row['STAGE_NAME'],
#                 stage_seq=row['STAGE_SEQ'],
#                 stage_date=row['STAGE_DATE'],
#                 t_clm_nbr=row['T_CLM_NBR'],
#                 c_lob=row['C_LOB'],
#                 c_lob_ctgry=row['C_LOB_CTGRY'],
#                 market_segment=row['MARKET_SEGMENT'],
#                 input_method=row['INPUT_METHOD'],
#                 aim_office=row['AIM_OFFICE'],
#                 claim_owner=row['CLAIM_OWNER'],
#                 claim_supervisor=row['CLAIM_SUPERVISOR']
#             )
#             db.session.add(claim)

#         db.session.commit()

#     except Exception as e:
#         print(f"Error loading CSV to DB: {e}")

# # Endpoint to get the count of claims grouped by c_lob and month
# @app.route('/lob-stage-count', methods=['GET'])
# def get_lob_stage_count():
#     try:
#         result = db.session.query(
#             Claim.c_lob,
#             Claim.stage_name,
#             db.func.strftime('%Y-%m', Claim.stage_date).label('month'),
#             db.func.count(Claim.id).label('count')
#         ).group_by(Claim.c_lob, Claim.stage_name, db.func.strftime('%Y-%m', Claim.stage_date)).all()

#         output = [{'c_lob': row.c_lob, 'stage_name': row.stage_name, 'month': row.month, 'count': row.count} for row in result]
#         return jsonify(output)

#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

# @app.route('/claims-stage-distribution', methods=['GET'])
# def get_claims_stage_distribution():
#     try:
#         # Query to count the number of claims for each stage
#         result = db.session.query(
#             Claim.stage_name,
#             db.func.count(Claim.id).label('count')
#         ).group_by(Claim.stage_name).all()

#         # Format the result as a list of dictionaries
#         output = [{'stage_name': row.stage_name, 'count': row.count} for row in result]

#         # Return the JSON response
#         return jsonify(output)

#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

# @app.route('/lob-vs-time', methods=['GET'])
# def get_lob_vs_time():
#     time_period = request.args.get('time_period', 'month')
    
#     if time_period == 'week':
#         time_format = '%Y-%U'
#     elif time_period == 'year':
#         time_format = '%Y'
#     else:  # Default to month
#         time_format = '%Y-%m'
    
#     try:
#         result = db.session.query(
#             Claim.c_lob,
#             db.func.strftime(time_format, Claim.stage_date).label('time_period'),
#             db.func.count(Claim.id).label('count')
#         ).group_by(Claim.c_lob, db.func.strftime(time_format, Claim.stage_date)).all()

#         output = []
#         for lob, time_period, count in result:
#             output.append({'c_lob': lob, 'time_period': time_period, 'count': count})

#         return jsonify(output)

#     except Exception as e:
#         return jsonify({'error': str(e)}), 500


#     try:
#         result = db.session.query(Claim.c_lob_ctgry).distinct().all()
#         categories = [row[0] for row in result]
#         return jsonify({'categories': categories})

#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

# @app.route('/lob-claims-data', methods=['GET'])
# def lob_claims_data():
#     try:
#         # Get the LOB from the request or set it to a default value
#         lob = request.args.get('lob', default='', type=str)

#         # Queries to get the count of claims for each stage for the selected LOB
#         total_claims = db.session.query(db.func.count(Claim.id)).filter(Claim.c_lob == lob).scalar()
#         loaded_claims = db.session.query(db.func.count(Claim.id)).filter(Claim.c_lob == lob, Claim.stage_name == 'CLAIM_LOADED').scalar()
#         recv_claims = db.session.query(db.func.count(Claim.id)).filter(Claim.c_lob == lob, Claim.stage_name == 'CLAIM_RECV\'D').scalar()
#         submitted_claims = db.session.query(db.func.count(Claim.id)).filter(Claim.c_lob == lob, Claim.stage_name == 'CLAIM_SUBMITTED').scalar()
#         assigned_claims = db.session.query(db.func.count(Claim.id)).filter(Claim.c_lob == lob, Claim.stage_name == 'CLAIM_ASSIGNED').scalar()
#         approved_claims = db.session.query(db.func.count(Claim.id)).filter(Claim.c_lob == lob, Claim.stage_name == 'CLAIM_APPROVED').scalar()
#         paid_claims = db.session.query(db.func.count(Claim.id)).filter(Claim.c_lob == lob, Claim.stage_name == 'CLAIM_PAID').scalar()
#         closed_claims = db.session.query(db.func.count(Claim.id)).filter(Claim.c_lob == lob, Claim.stage_name == 'CLAIM_CLOSED').scalar()
#         reopened_claims = db.session.query(db.func.count(Claim.id)).filter(Claim.c_lob == lob, Claim.stage_name == 'CLAIM_REOPENED').scalar()
#         processed_claims = db.session.query(db.func.count(Claim.id)).filter(Claim.c_lob == lob, Claim.stage_name == 'CLAIM_PROCESSED').scalar()
#         met_sla_claims = db.session.query(db.func.count(Claim.id)).filter(Claim.c_lob == lob, Claim.stage_name == 'CLAIM_MET_SLA').scalar()
#         reached_sla_claims = db.session.query(db.func.count(Claim.id)).filter(Claim.c_lob == lob, Claim.stage_name == 'CLAIM_MET_SCA').scalar()

#         # Return the JSON response with all stage counts
#         return jsonify({
#             'total_claims': total_claims,
#             'loaded_claims': loaded_claims,
#             'recv_claims': recv_claims,
#             'submitted_claims': submitted_claims,
#             'assigned_claims': assigned_claims,
#             'approved_claims': approved_claims,
#             'paid_claims': paid_claims,
#             'closed_claims': closed_claims,
#             'reopened_claims': reopened_claims,
#             'processed_claims': processed_claims,
#             'met_sla_claims': met_sla_claims,
#             'reached_sla_claims': reached_sla_claims
#         })
    
#     except Exception as e:
#         # Handle the exception and return an error response
#         return jsonify({'error': str(e)}), 500

# @app.route('/lob-vs-stage', methods=['GET'])
# def get_lob_vs_stage():
#     try:
#         # Perform the query
#         results = db.session.query(
#             Claim.stage_name,
#             Claim.c_lob,
#             db.func.count(Claim.id).label('count')
#         ).group_by(Claim.stage_name, Claim.c_lob).order_by(Claim.stage_name, Claim.c_lob).all()

#         # Format the results into a list of dictionaries
#         data = [{'stage_name': row.stage_name, 'c_lob': row.c_lob, 'count': row.count} for row in results]
        
#         # Return the JSON response
#         return jsonify(data)
        
#     except Exception as e:
#         # Return error message if there's an exception
#         return jsonify({'error': str(e)}), 500
        
# if __name__ == '__main__':
#     with app.app_context():
#         # Create the database and the tables
#         db.create_all()

#         # Load CSV data into the database (if needed)
#         load_csv_to_db()

#     app.run(debug=True)

# from flask import Flask, jsonify, request
# from flask_sqlalchemy import SQLAlchemy
# from flask_cors import CORS
# from datetime import datetime, timedelta
# from sqlalchemy import func
# import pandas as pd
# from sqlalchemy import extract
# from huggingface_hub import login
# import torch
# from transformers import LlamaForCausalLM, LlamaTokenizer, AutoTokenizer, pipeline
# from accelerate import init_empty_weights

# app = Flask(__name__)
# CORS(app)

# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///claim.db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# db = SQLAlchemy(app)

# class Claim(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     g_loss = db.Column(db.String(100))
#     stage_name = db.Column(db.String(100))
#     stage_seq = db.Column(db.Integer)
#     stage_date = db.Column(db.DateTime)
#     t_clm_nbr = db.Column(db.String(100))
#     c_lob = db.Column(db.String(100))
#     c_lob_ctgry = db.Column(db.String(100))
#     market_segment = db.Column(db.String(100))
#     input_method = db.Column(db.String(100))
#     aim_office = db.Column(db.String(100))
#     claim_owner = db.Column(db.String(100))
#     claim_supervisor = db.Column(db.String(100))
#     time_taken =  db.Column(db.Integer)

#     def __init__(self, g_loss, stage_name, stage_seq, stage_date, t_clm_nbr, c_lob, c_lob_ctgry, market_segment, input_method, aim_office, claim_owner, claim_supervisor, time_taken):
#         self.g_loss = g_loss
#         self.stage_name = stage_name
#         self.stage_seq = stage_seq
#         self.stage_date = stage_date
#         self.t_clm_nbr = t_clm_nbr
#         self.c_lob = c_lob
#         self.c_lob_ctgry = c_lob_ctgry
#         self.market_segment = market_segment
#         self.input_method = input_method
#         self.aim_office = aim_office
#         self.claim_owner = claim_owner
#         self.claim_supervisor = claim_supervisor
#         self.time_taken = time_taken
        
# # Helper function to calculate average count
# def calculate_average_count(time_range=None, lob=None, c_lob=None):
#     query = db.session.query(func.count(Claim.id))
#     if time_range:
#         query = query.filter(Claim.stage_date >= time_range)
#     if lob:
#         query = query.filter(Claim.c_lob == lob)
#     if c_lob:
#         query = query.filter(Claim.c_lob == c_lob)
#     return query.scalar()

# model_name = "gpt2"  
# nlp_pipeline = pipeline("text-generation", model=model_name)

# @app.route('/gpt-prompt', methods=['POST'])
# def classify_text():
#     data = request.json
#     input_text = data.get('input')
#     if not input_text:
#         return jsonify({"error": "No input text provided"}), 400
#     result = nlp_pipeline(input_text, max_length=500, num_return_sequences=1, temperature=0.7)
#     return jsonify(result)

# # model_id = "meta-llama/Meta-Llama-3.1-8B-Instruct"
# # pipe = pipeline("text-generation", model=model_id, model_kwargs={"torch_dtype": torch.bfloat16}, device="cuda")
# # llama 8b
# # model_name = "meta-llama/Llama-3.1-8B-Instruct" 
# # tokenizer = AutoTokenizer.from_pretrained(model_name)
# # model = AutoModelForCausalLM.from_pretrained(model_name)
# # text_generator = pipeline("text-generation", model=model, tokenizer=tokenizer)
# # @app.route('/generate', methods=['POST'])
# # def generate_text():
# #     data = request.json
# #     prompt = data.get('prompt', '')
# #     max_length = data.get('max_length', 100)
# #     if not prompt:
# #         return jsonify({"error": "Prompt is required"}), 400
# #     result = text_generator(prompt, max_length=max_length)
# #     return jsonify(result), 200

# # Endpoint to get Card 1 Data
# @app.route('/getCard1', methods=['GET'])
# def get_card1():
#     claims_received = db.session.query(func.count(Claim.id)).filter(Claim.stage_seq == 0).scalar()
#     return jsonify({"claims_received": claims_received})

# # Endpoint to get Card 2 Data (Average)
# @app.route('/getCard2', methods=['GET'])
# def get_card2():
#     today = datetime.now().date()
#     current_month_start = today.replace(day=1)

#     average_today = calculate_average_count(today)
#     average_current_month = calculate_average_count(current_month_start)

#     return jsonify({
#         "average_today": average_today,
#         "average_current_month": average_current_month
#     })

# @app.route('/unique-clob', methods=['GET'])
# def get_unique_clob():
#     unique_clobs = db.session.query(Claim.c_lob).distinct().all()
#     unique_clob_list = [clob[0] for clob in unique_clobs]
#     return jsonify(unique_clob_list)

# @app.route('/stage-wise-count', methods=['GET'])
# def get_stage_wise_count():
#     results = db.session.query(Claim.stage_name, db.func.count(Claim.id)).group_by(Claim.stage_name).all()
#     stage_wise_count = {stage_name: count for stage_name, count in results}
#     return jsonify(stage_wise_count)

# @app.route('/getCard3', methods=['GET'])
# def get_card3():
#     today = datetime.now().date()
#     yesterday = today - timedelta(days=1)
    
#     # Query for claims processed today
#     claims_processed_today = db.session.query(func.count(Claim.id)).filter(
#         Claim.stage_date == str(today),
#         Claim.stage_name == 'STAGE_PROCESSED'
#     ).scalar()

#     # Query for claims processed yesterday
#     claims_processed_yesterday = db.session.query(func.count(Claim.id)).filter(
#         Claim.stage_date == str(yesterday),
#         Claim.stage_name == 'STAGE_PROCESSED'
#     ).scalar()

#     return jsonify({
#         "claims_processed_today": claims_processed_today,
#         "claims_processed_yesterday": claims_processed_yesterday
#     })

# # Endpoint to get Card 4 Data (Stats Overall with Percentage)
# @app.route('/getCard4', methods=['GET'])
# def get_card4():
#     total_claims = db.session.query(func.count(Claim.id)).scalar()
#     claims_processed = db.session.query(func.count(Claim.id)).filter(Claim.stage_name == 'STAGE_PROCESSED').scalar()
#     processed_percentage = (claims_processed / total_claims) * 100 if total_claims else 0

#     return jsonify({
#         "total_claims": total_claims,
#         "claims_processed": claims_processed,
#         "processed_percentage": processed_percentage
#     })

# # Endpoints to get card data by specific c_lob
# @app.route('/getCard1ByC_LobId', methods=['GET'])
# def get_card1_by_c_lob():
#     c_lob = request.args.get('c_lob')
#     upcoming_claims = db.session.query(func.count(Claim.id)).filter(Claim.c_lob == c_lob, Claim.stage_seq == 0).scalar()
#     return jsonify({"upcoming_claims": upcoming_claims})

# def calculate_lob_average(c_lob):
#     records = Claim.query.filter_by(c_lob=c_lob).all()
#     if not records:
#         return None  # Or handle the case where there are no records

#     now = datetime.now()
#     days = [(now - record.created_at).days for record in records]
#     average_days = sum(days) / len(days)
#     return average_days
    
# # @app.route('/getCard2ByC_LobId', methods=['GET'])
# # def get_card2_by_c_lob():
# #     c_lob = request.args.get('c_lob')
# #     today = datetime.now().date()
# #     current_month_start = today.replace(day=1)

# #     average_today = calculate_average_count(today, c_lob=c_lob)
# #     average_current_month = calculate_average_count(current_month_start, c_lob=c_lob)

# #     return jsonify({
# #         "average_today": average_today,
# #         "average_current_month": average_current_month
# #     })

# @app.route('/getCard2ByC_LobId', methods=['GET'])
# def get_card2_by_c_lob():
#     c_lob = request.args.get('c_lob')
#     today = datetime.now().date()
#     current_month_start = today.replace(day=1)

#     # Calculate the averages
#     average_today = calculate_average_count(today, c_lob=c_lob)
#     average_current_month = calculate_average_count(current_month_start, c_lob=c_lob)
    
#     # Calculate the lob average
#     lob_average = calculate_lob_average(c_lob=c_lob)

#     return jsonify({
#         "average_today": average_today,
#         "average_current_month": average_current_month,
#         "lob_average": lob_average
#     })

# @app.route('/getCard3ByC_LobId', methods=['GET'])
# def get_card3_by_c_lob():
#     c_lob = request.args.get('c_lob')
#     today = datetime.now().date()
#     claims_processed_today = db.session.query(func.count(Claim.id)).filter(Claim.c_lob == c_lob, Claim.stage_date == str(today), Claim.stage_name == 'STAGE_PROCESSED').scalar()
#     return jsonify({"claims_processed_today": claims_processed_today})

# @app.route('/getCard4ByC_LobId', methods=['GET'])
# def get_card4_by_c_lob():
#     c_lob = request.args.get('c_lob')
#     total_claims = db.session.query(func.count(Claim.id)).filter(Claim.c_lob == c_lob).scalar()
#     claims_processed = db.session.query(func.count(Claim.id)).filter(Claim.c_lob == c_lob, Claim.stage_name == 'STAGE_PROCESSED').scalar()
#     processed_percentage = (claims_processed / total_claims) * 100 if total_claims else 0

#     return jsonify({
#         "total_claims": total_claims,
#         "claims_processed": claims_processed,
#         "processed_percentage": processed_percentage
#     })

# @app.route('/lob-claims-stats', methods=['GET'])
# def get_lob_claims_stats():
#     c_lob = request.args.get('c_lob', default=None, type=str)
#     month = request.args.get('month', default=None, type=int)
#     year = request.args.get('year', default=None, type=int)

#     query = db.session.query(
#         Claim.c_lob,
#         func.strftime('%Y-%m', Claim.stage_date).label('month_year'),
#         func.count(Claim.id).label('count')
#     )

#     if c_lob:
#         query = query.filter(Claim.c_lob == c_lob)
    
#     if month and year:
#         start_date = datetime(year, month, 1).date()
#         next_month = (start_date.replace(day=28) + timedelta(days=4)).replace(day=1)
#         end_date = (next_month - timedelta(days=1)).date()
#         query = query.filter(Claim.stage_date >= start_date, Claim.stage_date <= end_date)
    
#     results = query.group_by(Claim.c_lob, 'month_year').all()
    
#     lob_claims_stats = {}
#     for lob, month_year, count in results:
#         if lob not in lob_claims_stats:
#             lob_claims_stats[lob] = {}
#         lob_claims_stats[lob][month_year] = count

#     return jsonify(lob_claims_stats)

# @app.route('/stage-aggregation', methods=['GET'])
# def stage_aggregation():
#     results = db.session.query(
#         Claim.stage_name,
#         func.count(Claim.id).label('count')
#     ).group_by(Claim.stage_name).all()

#     stage_counts = {stage_name: count for stage_name, count in results}
#     return jsonify(stage_counts)

# @app.route('/stage-aggregation-by-c-lob', methods=['GET'])
# def stage_aggregation_by_c_lob():
#     c_lob = request.args.get('c_lob', default=None, type=str)

#     query = db.session.query(
#         Claim.stage_name,
#         func.count(Claim.id).label('count')
#     )

#     if c_lob:
#         query = query.filter(Claim.c_lob == c_lob)

#     results = query.group_by(Claim.stage_name).all()

#     stage_counts = {stage_name: count for stage_name, count in results}
#     return jsonify(stage_counts)

# @app.route('/claims/lob-market-segment-aggregate', methods=['GET'])
# def get_lob_market_segment_aggregate():
#     # Example data aggregation query
#     result = db.session.query(
#         Claim.c_lob,
#         Claim.market_segment,
#         db.func.count(Claim.id).label('count')
#     ).group_by(Claim.c_lob, Claim.market_segment).all()

#     data = {}
#     for lob, market_segment, count in result:
#         if lob not in data:
#             data[lob] = {}
#         data[lob][market_segment] = count

#     return jsonify(data)

# @app.route('/claims/lob-owner-aggregate', methods=['GET'])
# def get_lob_owner_aggregate():
#     # Example data aggregation query
#     result = db.session.query(
#         Claim.c_lob,
#         Claim.claim_owner,
#         db.func.count(Claim.id).label('count')
#     ).group_by(Claim.c_lob, Claim.claim_owner).all()

#     data = {}
#     for lob, owner, count in result:
#         if lob not in data:
#             data[lob] = {}
#         data[lob][owner] = count

#     return jsonify(data)

# @app.route('/claims/lob-supervisor-aggregate', methods=['GET'])
# def get_lob_supervisor_aggregate():
#     # Example data aggregation query
#     result = db.session.query(
#         Claim.c_lob,
#         Claim.claim_supervisor,
#         db.func.count(Claim.id).label('count')
#     ).group_by(Claim.c_lob, Claim.claim_supervisor).all()

#     data = {}
#     for lob, supervisor, count in result:
#         if lob not in data:
#             data[lob] = {}
#         data[lob][supervisor] = count

#     return jsonify(data)

# @app.route('/aggregate-data', methods=['GET'])
# def get_aggregate_data():
#     data = {
#         'lob': {},
#         'market_segment': {},
#         'owner': {},
#         'supervisor': {}
#     }

#     # Aggregate by LOB
#     lob_result = db.session.query(Claim.c_lob, db.func.count(Claim.id)).group_by(Claim.c_lob).all()
#     for lob, count in lob_result:
#         data['lob'][lob] = count

#     # Aggregate by Market Segment
#     market_segment_result = db.session.query(Claim.market_segment, db.func.count(Claim.id)).group_by(Claim.market_segment).all()
#     for segment, count in market_segment_result:
#         data['market_segment'][segment] = count

#     # Aggregate by Owner
#     owner_result = db.session.query(Claim.claim_owner, db.func.count(Claim.id)).group_by(Claim.claim_owner).all()
#     for owner, count in owner_result:
#         data['owner'][owner] = count

#     # Aggregate by Supervisor
#     supervisor_result = db.session.query(Claim.claim_supervisor, db.func.count(Claim.id)).group_by(Claim.claim_supervisor).all()
#     for supervisor, count in supervisor_result:
#         data['supervisor'][supervisor] = count

#     return jsonify(data)

# @app.route('/claims-stage-monthly', methods=['GET'])
# def get_claims_stage_monthly():
#     # Get the start and end date from request arguments if provided
#     start_date = request.args.get('start_date', '2025-01-01')
#     end_date = request.args.get('end_date', '2025-12-31')

#     try:
#         # Convert to datetime objects for validation
#         start_date = datetime.strptime(start_date, '%Y-%m-%d')
#         end_date = datetime.strptime(end_date, '%Y-%m-%d')

#         results = db.session.query(
#             Claim.stage_name,
#             func.strftime('%Y-%m', Claim.stage_date).label('month_year'),
#             func.count(Claim.id).label('count')
#         ).filter(
#             Claim.stage_date >= start_date,
#             Claim.stage_date <= end_date
#         ).group_by(
#             Claim.stage_name,
#             'month_year'
#         ).all()

#         # Process results into a dictionary
#         data = {}
#         for stage_name, month_year, count in results:
#             if stage_name not in data:
#                 data[stage_name] = {}
#             data[stage_name][month_year] = count

#         # Fill in missing months for each stage
#         all_months = {f'{start_date.year}-{month:02d}' for month in range(1, 13)}
#         for stage in data:
#             for month in all_months:
#                 if month not in data[stage]:
#                     data[stage][month] = 0

#         # Convert to a format suitable for a heatmap
#         formatted_data = {
#             'months': sorted(all_months),
#             'stages': list(data.keys()),
#             'matrix': [[data[stage].get(month, 0) for month in sorted(all_months)] for stage in data.keys()]
#         }

#         return jsonify(formatted_data)

#     except ValueError as e:
#         return jsonify({'error': f'Invalid date format: {e}'}), 400

# @app.route('/stage-progression', methods=['GET'])
# def get_stage_progression():
#     # Query to get claim stage data ordered by claim number and stage sequence
#     claim_stages = db.session.query(
#         Claim.t_clm_nbr, Claim.stage_seq, Claim.stage_date
#     ).order_by(Claim.t_clm_nbr, Claim.stage_seq).all()

#     progression_data = []
#     claim_stage_map = {}

#     # Organizing data by claim number
#     for t_clm_nbr, stage_seq, stage_date in claim_stages:
#         date_obj = stage_date  # stage_date is already a datetime object

#         if t_clm_nbr not in claim_stage_map:
#             claim_stage_map[t_clm_nbr] = []

#         claim_stage_map[t_clm_nbr].append({
#             "stage_seq": stage_seq,
#             "stage_date": date_obj
#         })

#     # Calculate time differences between stages
#     for t_clm_nbr, stages in claim_stage_map.items():
#         for i in range(1, len(stages)):
#             prev_stage = stages[i-1]
#             curr_stage = stages[i]

#             # Calculate time difference (in days) between current and previous stage
#             duration = (curr_stage["stage_date"] - prev_stage["stage_date"]).days

#             progression_data.append({
#                 "claim_id": t_clm_nbr,
#                 "stage_seq": curr_stage["stage_seq"],
#                 "duration": duration
#             })

#     return jsonify(progression_data)

# @app.route('/get-all-claims', methods=['GET'])
# def get_all_claims():
#     try:
#         # Query to get all claims from the database
#         claims = db.session.query(Claim).all()

#         # Serialize the results into a list of dictionaries
#         claims_list = []
#         for claim in claims:
#             claim_dict = {
#                 'id': claim.id,
#                 'g_loss': claim.g_loss,
#                 'stage_name': claim.stage_name,
#                 'stage_seq': claim.stage_seq,
#                 'stage_date': claim.stage_date,
#                 't_clm_nbr': claim.t_clm_nbr,
#                 'c_lob': claim.c_lob,
#                 'c_lob_ctgry': claim.c_lob_ctgry,
#                 'market_segment': claim.market_segment,
#                 'input_method': claim.input_method,
#                 'aim_office': claim.aim_office,
#                 'claim_owner': claim.claim_owner,
#                 'claim_supervisor': claim.claim_supervisor,
#                 'time_taken': claim.time_taken
#             }
#             claims_list.append(claim_dict)

#         return jsonify(claims_list)

#     except Exception as e:
#         return jsonify({'error': str(e)}), 500


# if __name__ == '__main__':
#     app.run(debug=True)

# if __name__ == '__main__':
#     with app.app_context():
#         db.create_all()
#     app.run(debug=True)

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime, timedelta
from sqlalchemy import func
import pandas as pd
from sqlalchemy import extract
from huggingface_hub import login
import torch
from transformers import LlamaForCausalLM, LlamaTokenizer, AutoTokenizer, pipeline
from accelerate import init_empty_weights
from sqlalchemy import or_

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///claim.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Claim(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    g_loss = db.Column(db.String(100))
    stage_name = db.Column(db.String(100))
    stage_seq = db.Column(db.Integer)
    stage_date = db.Column(db.DateTime)
    t_clm_nbr = db.Column(db.String(100))
    c_lob = db.Column(db.String(100))
    c_lob_ctgry = db.Column(db.String(100))
    market_segment = db.Column(db.String(100))
    input_method = db.Column(db.String(100))
    aim_office = db.Column(db.String(100))
    claim_owner = db.Column(db.String(100))
    claim_supervisor = db.Column(db.String(100))
    time_taken =  db.Column(db.Integer)

    def __init__(self, g_loss, stage_name, stage_seq, stage_date, t_clm_nbr, c_lob, c_lob_ctgry, market_segment, input_method, aim_office, claim_owner, claim_supervisor, time_taken):
        self.g_loss = g_loss
        self.stage_name = stage_name
        self.stage_seq = stage_seq
        self.stage_date = stage_date
        self.t_clm_nbr = t_clm_nbr
        self.c_lob = c_lob
        self.c_lob_ctgry = c_lob_ctgry
        self.market_segment = market_segment
        self.input_method = input_method
        self.aim_office = aim_office
        self.claim_owner = claim_owner
        self.claim_supervisor = claim_supervisor
        self.time_taken = time_taken
        
# Helper function to calculate average count
def calculate_average_count(time_range=None, lob=None, c_lob=None):
    query = db.session.query(func.count(Claim.id))
    if time_range:
        query = query.filter(Claim.stage_date >= time_range)
    if lob:
        query = query.filter(Claim.c_lob == lob)
    if c_lob:
        query = query.filter(Claim.c_lob == c_lob)
    return query.scalar()

model_name = "gpt2"  
nlp_pipeline = pipeline("text-generation", model=model_name)

@app.route('/gpt-prompt', methods=['POST'])
def classify_text():
    data = request.json
    input_text = data.get('input')
    if not input_text:
        return jsonify({"error": "No input text provided"}), 400
    result = nlp_pipeline(input_text, max_length=300, num_return_sequences=1, temperature=0.7)
    return jsonify(result)

# model_id = "meta-llama/Meta-Llama-3.1-8B-Instruct"
# pipe = pipeline("text-generation", model=model_id, model_kwargs={"torch_dtype": torch.bfloat16}, device="cuda")
# llama 8b
# model_name = "meta-llama/Llama-3.1-8B-Instruct" 
# tokenizer = AutoTokenizer.from_pretrained(model_name)
# model = AutoModelForCausalLM.from_pretrained(model_name)
# text_generator = pipeline("text-generation", model=model, tokenizer=tokenizer)
# @app.route('/generate', methods=['POST'])
# def generate_text():
#     data = request.json
#     prompt = data.get('prompt', '')
#     max_length = data.get('max_length', 100)
#     if not prompt:
#         return jsonify({"error": "Prompt is required"}), 400
#     result = text_generator(prompt, max_length=max_length)
#     return jsonify(result), 200

# Endpoint to get Card 1 Data
@app.route('/getCard1', methods=['GET'])
def get_card1():
    claim_pending = db.session.query(func.count(Claim.id)).filter(Claim.stage_seq == 1).scalar()
    sla_breached = db.session.query(func.count(Claim.id)).filter(Claim.stage_seq == 2).scalar()
    
    return jsonify({"claim_pending": claim_pending, "sla_breached": sla_breached})

# Endpoint to get Card 2 Data (Average)
@app.route('/getCard2', methods=['GET'])
def get_card2():
    today = datetime.now().date()
    current_month_start = today.replace(day=1)

    average_today = calculate_average_count(today)
    average_current_month = calculate_average_count(current_month_start)

    # Calculate LOB Average
    lob_average = (
        db.session.query(func.avg(Claim.c_lob))  # Replace 'lob_field' with your actual LOB field name
        .filter(Claim.stage_date >= current_month_start)  # Assuming 'created_at' is the date field for claims
        .scalar(),
    )

    # # Calculate Region Average
    # region_average = (
    #     db.session.query(func.avg(Claim.region))  # Replace 'region_field' with your actual region field name
    #     .filter(Claim.stage_date >= current_month_start)  # Same assumption for 'created_at'
    #     .scalar()
    # )

    return jsonify({
        "average_today": average_today,
        "average_current_month": average_current_month,
        "lob_average": lob_average,
        # "region_average": region_average
    })

@app.route('/getCard3', methods=['GET'])
def get_card3():
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)
    
    # Query for claims processed today
    claims_processed_today = db.session.query(func.count(Claim.id)).filter(
        Claim.stage_date == str(today),
        Claim.stage_name == 'CLAIM_PROCESSED'
    ).scalar()

    # Query for claims processed yesterday
    claims_processed_yesterday = db.session.query(func.count(Claim.id)).filter(
        Claim.stage_date == str(yesterday),
        Claim.stage_name == 'CLAIM_PROCESSED'
    ).scalar()

    return jsonify({
        "claims_processed_today": claims_processed_today,
        "claims_processed_yesterday": claims_processed_yesterday
    })

# Endpoint to get Card 4 Data (Stats Overall with Percentage)
@app.route('/getCard4', methods=['GET'])
def get_card4():
    total_claims = db.session.query(func.count(Claim.id)).scalar()
    claims_processed = db.session.query(func.count(Claim.id)).filter(Claim.stage_name == 'CLAIM_PROCESSED').scalar()
    processed_percentage = (claims_processed / total_claims) * 100 if total_claims else 0

    return jsonify({
        "total_claims": total_claims,
        "claims_processed": claims_processed,
        "processed_percentage": processed_percentage
    })

# Endpoints to get card data by specific c_lob
@app.route('/getCard1ByC_LobId', methods=['GET'])
def get_card1_by_c_lob():
    c_lob = request.args.get('c_lob')
    upcoming_claims = db.session.query(func.count(Claim.id)).filter(Claim.c_lob == c_lob, Claim.stage_seq == 0).scalar()
    return jsonify({"upcoming_claims": upcoming_claims})

def calculate_lob_average(c_lob):
    records = Claim.query.filter_by(c_lob=c_lob).all()
    if not records:
        return None  # Or handle the case where there are no records

    now = datetime.now()
    days = [(now - record.created_at).days for record in records]
    average_days = sum(days) / len(days)
    return average_days
    
# @app.route('/getCard2ByC_LobId', methods=['GET'])
# def get_card2_by_c_lob():
#     c_lob = request.args.get('c_lob')
#     today = datetime.now().date()
#     current_month_start = today.replace(day=1)

#     average_today = calculate_average_count(today, c_lob=c_lob)
#     average_current_month = calculate_average_count(current_month_start, c_lob=c_lob)

#     return jsonify({
#         "average_today": average_today,
#         "average_current_month": average_current_month
#     })

@app.route('/getCard2ByC_LobId', methods=['GET'])
def get_card2_by_c_lob():
    c_lob = request.args.get('c_lob')
    today = datetime.now().date()
    current_month_start = today.replace(day=1)

    # Calculate the averages
    average_today = calculate_average_count(today, c_lob=c_lob)
    average_current_month = calculate_average_count(current_month_start, c_lob=c_lob)
    
    # Calculate the lob average
    lob_average = calculate_lob_average(c_lob=c_lob)

    return jsonify({
        "average_today": average_today,
        "average_current_month": average_current_month,
        "lob_average": lob_average
    })

@app.route('/getCard3ByC_LobId', methods=['GET'])
def get_card3_by_c_lob():
    c_lob = request.args.get('c_lob')
    today = datetime.now().date()
    claims_processed_today = db.session.query(func.count(Claim.id)).filter(Claim.c_lob == c_lob, Claim.stage_date == str(today), Claim.stage_name == 'STAGE_PROCESSED').scalar()
    return jsonify({"claims_processed_today": claims_processed_today})

@app.route('/getCard4ByC_LobId', methods=['GET'])
def get_card4_by_c_lob():
    c_lob = request.args.get('c_lob')
    total_claims = db.session.query(func.count(Claim.id)).filter(Claim.c_lob == c_lob).scalar()
    claims_processed = db.session.query(func.count(Claim.id)).filter(Claim.c_lob == c_lob, Claim.stage_name == 'STAGE_PROCESSED').scalar()
    processed_percentage = (claims_processed / total_claims) * 100 if total_claims else 0

    return jsonify({
        "total_claims": total_claims,
        "claims_processed": claims_processed,
        "processed_percentage": processed_percentage
    })


@app.route('/unique-clob', methods=['GET'])
def get_unique_clob():
    unique_clobs = db.session.query(Claim.c_lob).distinct().all()
    unique_clob_list = [clob[0] for clob in unique_clobs]
    return jsonify(unique_clob_list)

@app.route('/stage-wise-count', methods=['GET'])
def get_stage_wise_count():
    results = db.session.query(Claim.stage_name, db.func.count(Claim.id)).group_by(Claim.stage_name).all()
    stage_wise_count = {stage_name: count for stage_name, count in results}
    return jsonify(stage_wise_count)

@app.route('/lob-claims-stats', methods=['GET'])
def get_lob_claims_stats():
    c_lob = request.args.get('c_lob', default=None, type=str)
    month = request.args.get('month', default=None, type=int)
    year = request.args.get('year', default=None, type=int)

    query = db.session.query(
        Claim.c_lob,
        func.strftime('%Y-%m', Claim.stage_date).label('month_year'),
        func.count(Claim.id).label('count')
    )

    if c_lob:
        query = query.filter(Claim.c_lob == c_lob)
    
    if month and year:
        start_date = datetime(year, month, 1).date()
        next_month = (start_date.replace(day=28) + timedelta(days=4)).replace(day=1)
        end_date = (next_month - timedelta(days=1)).date()
        query = query.filter(Claim.stage_date >= start_date, Claim.stage_date <= end_date)
    
    results = query.group_by(Claim.c_lob, 'month_year').all()
    
    lob_claims_stats = {}
    for lob, month_year, count in results:
        if lob not in lob_claims_stats:
            lob_claims_stats[lob] = {}
        lob_claims_stats[lob][month_year] = count

    return jsonify(lob_claims_stats)

@app.route('/stage-aggregation', methods=['GET'])
def stage_aggregation():
    results = db.session.query(
        Claim.stage_name,
        func.count(Claim.id).label('count')
    ).group_by(Claim.stage_name).all()

    stage_counts = {stage_name: count for stage_name, count in results}
    return jsonify(stage_counts)

@app.route('/stage-aggregation-by-c-lob', methods=['GET'])
def stage_aggregation_by_c_lob():
    c_lob = request.args.get('c_lob', default=None, type=str)

    query = db.session.query(
        Claim.stage_name,
        func.count(Claim.id).label('count')
    )

    if c_lob:
        query = query.filter(Claim.c_lob == c_lob)

    results = query.group_by(Claim.stage_name).all()

    stage_counts = {stage_name: count for stage_name, count in results}
    return jsonify(stage_counts)

@app.route('/claims/lob-market-segment-aggregate', methods=['GET'])
def get_lob_market_segment_aggregate():
    # Example data aggregation query
    result = db.session.query(
        Claim.c_lob,
        Claim.market_segment,
        db.func.count(Claim.id).label('count')
    ).group_by(Claim.c_lob, Claim.market_segment).all()

    data = {}
    for lob, market_segment, count in result:
        if lob not in data:
            data[lob] = {}
        data[lob][market_segment] = count

    return jsonify(data)

@app.route('/claims/lob-owner-aggregate', methods=['GET'])
def get_lob_owner_aggregate():
    # Example data aggregation query
    result = db.session.query(
        Claim.c_lob,
        Claim.claim_owner,
        db.func.count(Claim.id).label('count')
    ).group_by(Claim.c_lob, Claim.claim_owner).all()

    data = {}
    for lob, owner, count in result:
        if lob not in data:
            data[lob] = {}
        data[lob][owner] = count

    return jsonify(data)

@app.route('/claims/lob-supervisor-aggregate', methods=['GET'])
def get_lob_supervisor_aggregate():
    # Example data aggregation query
    result = db.session.query(
        Claim.c_lob,
        Claim.claim_supervisor,
        db.func.count(Claim.id).label('count')
    ).group_by(Claim.c_lob, Claim.claim_supervisor).all()

    data = {}
    for lob, supervisor, count in result:
        if lob not in data:
            data[lob] = {}
        data[lob][supervisor] = count

    return jsonify(data)

@app.route('/aggregate-data', methods=['GET'])
def get_aggregate_data():
    data = {
        'lob': {},
        'market_segment': {},
        'owner': {},
        'supervisor': {}
    }

    # Aggregate by LOB
    lob_result = db.session.query(Claim.c_lob, db.func.count(Claim.id)).group_by(Claim.c_lob).all()
    for lob, count in lob_result:
        data['lob'][lob] = count

    # Aggregate by Market Segment
    market_segment_result = db.session.query(Claim.market_segment, db.func.count(Claim.id)).group_by(Claim.market_segment).all()
    for segment, count in market_segment_result:
        data['market_segment'][segment] = count

    # Aggregate by Owner
    owner_result = db.session.query(Claim.claim_owner, db.func.count(Claim.id)).group_by(Claim.claim_owner).all()
    for owner, count in owner_result:
        data['owner'][owner] = count

    # Aggregate by Supervisor
    supervisor_result = db.session.query(Claim.claim_supervisor, db.func.count(Claim.id)).group_by(Claim.claim_supervisor).all()
    for supervisor, count in supervisor_result:
        data['supervisor'][supervisor] = count

    return jsonify(data)

@app.route('/claims-stage-monthly', methods=['GET'])
def get_claims_stage_monthly():
    # Get the start and end date from request arguments if provided
    start_date = request.args.get('start_date', '2025-01-01')
    end_date = request.args.get('end_date', '2025-12-31')

    try:
        # Convert to datetime objects for validation
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')

        results = db.session.query(
            Claim.stage_name,
            func.strftime('%Y-%m', Claim.stage_date).label('month_year'),
            func.count(Claim.id).label('count')
        ).filter(
            Claim.stage_date >= start_date,
            Claim.stage_date <= end_date
        ).group_by(
            Claim.stage_name,
            'month_year'
        ).all()

        # Process results into a dictionary
        data = {}
        for stage_name, month_year, count in results:
            if stage_name not in data:
                data[stage_name] = {}
            data[stage_name][month_year] = count

        # Fill in missing months for each stage
        all_months = {f'{start_date.year}-{month:02d}' for month in range(1, 13)}
        for stage in data:
            for month in all_months:
                if month not in data[stage]:
                    data[stage][month] = 0

        # Convert to a format suitable for a heatmap
        formatted_data = {
            'months': sorted(all_months),
            'stages': list(data.keys()),
            'matrix': [[data[stage].get(month, 0) for month in sorted(all_months)] for stage in data.keys()]
        }

        return jsonify(formatted_data)

    except ValueError as e:
        return jsonify({'error': f'Invalid date format: {e}'}), 400

@app.route('/stage-progression', methods=['GET'])
def get_stage_progression():
    # Query to get claim stage data ordered by claim number and stage sequence
    claim_stages = db.session.query(
        Claim.t_clm_nbr, Claim.stage_seq, Claim.stage_date
    ).order_by(Claim.t_clm_nbr, Claim.stage_seq).all()

    progression_data = []
    claim_stage_map = {}

    # Organizing data by claim number
    for t_clm_nbr, stage_seq, stage_date in claim_stages:
        date_obj = stage_date  # stage_date is already a datetime object

        if t_clm_nbr not in claim_stage_map:
            claim_stage_map[t_clm_nbr] = []

        claim_stage_map[t_clm_nbr].append({
            "stage_seq": stage_seq,
            "stage_date": date_obj
        })

    # Calculate time differences between stages
    for t_clm_nbr, stages in claim_stage_map.items():
        for i in range(1, len(stages)):
            prev_stage = stages[i-1]
            curr_stage = stages[i]

            # Calculate time difference (in days) between current and previous stage
            duration = (curr_stage["stage_date"] - prev_stage["stage_date"]).days

            progression_data.append({
                "claim_id": t_clm_nbr,
                "stage_seq": curr_stage["stage_seq"],
                "duration": duration
            })

    return jsonify(progression_data)

@app.route('/get-all-claims', methods=['GET'])
def get_all_claims():
    try:
        # Query to get all claims from the database
        claims = db.session.query(Claim).all()

        # Serialize the results into a list of dictionaries
        claims_list = []
        for claim in claims:
            claim_dict = {
                'id': claim.id,
                'g_loss': claim.g_loss,
                'stage_name': claim.stage_name,
                'stage_seq': claim.stage_seq,
                'stage_date': claim.stage_date,
                't_clm_nbr': claim.t_clm_nbr,
                'c_lob': claim.c_lob,
                'c_lob_ctgry': claim.c_lob_ctgry,
                'market_segment': claim.market_segment,
                'input_method': claim.input_method,
                'aim_office': claim.aim_office,
                'claim_owner': claim.claim_owner,
                'claim_supervisor': claim.claim_supervisor,
                'time_taken': claim.time_taken
            }
            claims_list.append(claim_dict)

        return jsonify(claims_list)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)