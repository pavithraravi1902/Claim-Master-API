from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, extract
from flask_cors import CORS
from flasgger import Swagger
from transformers import pipeline
from datetime import datetime, timedelta, timezone
import time

app = Flask(__name__)
Swagger(app)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///claim.db'  # Increased timeout
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
    time_taken = db.Column(db.Integer) 
    claims_pending = db.Column(db.Integer, default=0) 
    sla_breached = db.Column(db.Integer, default=0)  
    processing_time_today = db.Column(db.Integer)  
    processing_time_avg = db.Column(db.Integer) 
    claims_processed_today = db.Column(db.Integer)  
    claims_processed_month_to_date = db.Column(db.Integer)  
    total_claims = db.Column(db.Integer)  
    sla_met = db.Column(db.Integer)  
    abandoned = db.Column(db.Integer) 
    region = db.Column(db.String(100)) 

    def __init__(self, g_loss, stage_name, stage_seq, stage_date, t_clm_nbr, c_lob, c_lob_ctgry,
                 market_segment, input_method, aim_office, claim_owner, claim_supervisor,
                 time_taken, claims_pending, sla_breached, processing_time_today, processing_time_avg,
                 claims_processed_today, claims_processed_month_to_date, total_claims, sla_met, abandoned, region):
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
        self.claims_pending = claims_pending
        self.sla_breached = sla_breached
        self.processing_time_today = processing_time_today
        self.processing_time_avg = processing_time_avg
        self.claims_processed_today = claims_processed_today
        self.claims_processed_month_to_date = claims_processed_month_to_date
        self.total_claims = total_claims
        self.sla_met = sla_met
        self.abandoned = abandoned
        self.region = region

# Create the database and tables
with app.app_context():
    db.create_all()

@app.route('/create-claim', methods=['POST'])
def create_claim():
    try:
        data = request.get_json()

        c_lob_ctgry = data.get('c_lob_ctgry')
        claim_number = data.get('claim_number')
        stage_name = data.get('stage_name')
        time_taken = data.get('time_taken')
        claims_processed_today = data.get('claims_processed_today')
        stage_date_str = data.get('stage_date')
        region = data.get('region')

        if not all([c_lob_ctgry, claim_number, stage_name, time_taken, claims_processed_today, stage_date_str, region]):
            return jsonify({"error": "Missing required fields"}), 400

        try:
            stage_date = datetime.strptime(stage_date_str, '%Y-%m-%d')
        except ValueError:
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400

        new_claim = Claim(
            c_lob_ctgry=c_lob_ctgry,
            claim_number=claim_number,
            stage_name=stage_name,
            time_taken=time_taken,
            claims_processed_today=claims_processed_today,
            stage_date=stage_date,
            region=region
        )

        db.session.add(new_claim)
        db.session.commit()

        return jsonify({"message": "Claim created successfully", "claim_id": new_claim.id}), 201

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return jsonify({"error": "An error occurred while creating the claim"}), 500

@app.route('/unique-categories', methods=['GET'])
def get_unique_categories():
    try:
        unique_categories = db.session.query(Claim.c_lob_ctgry).distinct().all()
        categories_list = [category[0] for category in unique_categories]
        return jsonify(categories=categories_list), 200
    except Exception as e:
        return jsonify(error=str(e)), 500

@app.route('/unique-lobs', methods=['GET'])
def get_unique_lobs():
    try:
        unique_lobs = db.session.query(Claim.c_lob).distinct().all()
        lobs_list = [lob[0] for lob in unique_lobs]
        return jsonify(lobs=lobs_list), 200
    except Exception as e:
        return jsonify(error=str(e)), 500

@app.route('/test-insert', methods=['POST'])
def test_insert():
    max_retries = 10  
    for attempt in range(max_retries):
        try:
            claims = Claim.query.all()
            for claim in claims:
                if claim.stage_name in ['CLAIM_LOADED', 'CLAIM_REGISTERED']:
                    claim.claims_pending = (claim.claims_pending or 0) + 1
                if claim.time_taken is not None and claim.time_taken > 1:  
                    claim.sla_breached = (claim.sla_breached or 0) + 1
                claim.claims_processed_today = (claim.claims_processed_today or 0) + 1
                claim.claims_processed_month_to_date = (claim.claims_processed_month_to_date or 0) + 1

            db.session.commit()
            return jsonify({"message": "Claim inserted and metrics calculated."}), 200

        except Exception as e:
            db.session.rollback()  
            if "database is locked" in str(e):
                print(f"Database is locked, retrying... (attempt {attempt + 1})")
                time.sleep(1) 
                continue 
            return jsonify({"error": str(e)}), 500
    return jsonify({"error": "Max retries reached, database is still locked."}), 500

@app.route('/get-all-claims', methods=['GET'])
def get_all_claims():
    print("Received request for all claims") 
    claims = Claim.query.all()
    if not claims:
        return jsonify({"message": "No claims data found."}), 404
    claims_data = []
    for claim in claims:
        claims_data.append({
            "id": claim.id,
            "g_loss": claim.g_loss,
            "stage_name": claim.stage_name,
            "stage_seq": claim.stage_seq,
            "stage_date": claim.stage_date,
            "t_clm_nbr": claim.t_clm_nbr,
            "c_lob": claim.c_lob,
            "c_lob_ctgry": claim.c_lob_ctgry,
            "market_segment": claim.market_segment,
            "input_method": claim.input_method,
            "aim_office": claim.aim_office,
            "claim_owner": claim.claim_owner,
            "claim_supervisor": claim.claim_supervisor,
            "time_taken": claim.time_taken,
            "claims_pending": claim.claims_pending,
            "sla_breached": claim.sla_breached,
            "processing_time_today": claim.processing_time_today,
            "processing_time_avg": claim.processing_time_avg,
            "claims_processed_today": claim.claims_processed_today,
            "claims_processed_month_to_date": claim.claims_processed_month_to_date,
            "total_claims": claim.total_claims,
            "sla_met": claim.sla_met,
            "abandoned": claim.abandoned,
            "region": claim.region
        })

    return jsonify(claims_data), 200


@app.route('/getCard1', methods=['GET'])
def get_active_claims():
    try:
        active_claims = Claim.query.filter(
            Claim.claims_pending > 0 
        ).all()
        pending_claim_count = sum(claim.claims_pending or 0 for claim in active_claims)
        sla_breached_count = sum(claim.sla_breached or 0 for claim in active_claims)
        active_claims_data = []
        for claim in active_claims:
            active_claims_data.append({
                "id": claim.id,
                "g_loss": claim.g_loss,
                "stage_name": claim.stage_name,
                "stage_date": claim.stage_date.isoformat() if claim.stage_date else '',
                "t_clm_nbr": claim.t_clm_nbr,
                "c_lob": claim.c_lob,
                "claims_pending": claim.claims_pending or 0,
                "sla_breached": claim.sla_breached or 0,
                "time_taken": claim.time_taken or 0,
                "region": claim.region,
            })
        return jsonify({
            "claim_pending": pending_claim_count,
            "sla_breached": sla_breached_count
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# average-processing-time
@app.route('/getCard2', methods=['GET'])
def average_processing_time():
    try:
        today = datetime.now(timezone.utc).date()
        first_day_of_month = today.replace(day=1)
        print(today)
        print(first_day_of_month)
        start_of_today = datetime.combine(today, datetime.min.time(), tzinfo=timezone.utc)
        end_of_today = datetime.combine(today, datetime.max.time(), tzinfo=timezone.utc)
        today_avg = db.session.query(func.avg(Claim.time_taken)).filter(
            Claim.stage_date >= start_of_today,
            Claim.stage_date <= end_of_today
        ).scalar() or 0

        # Average processing time for the current month (using EXTRACT for month and year)
        month_avg = db.session.query(func.avg(Claim.time_taken)).filter(
            extract('month', Claim.stage_date) == today.month,
            extract('year', Claim.stage_date) == today.year
        ).scalar() or 0

        lob_count = db.session.query(
            Claim.c_lob,
            func.count(Claim.id) 
        ).group_by(Claim.c_lob).all()

        region_count = db.session.query(
            Claim.region,
            func.count(Claim.id) 
        ).group_by(Claim.region).all()
        response_data = {
            "today_average": round(today_avg),
            "month_average": round(month_avg),
            "lob_average": sum(count for lob, count in lob_count),
            "region_average": sum(count for region, count in region_count) 
        }

        return jsonify(response_data), 200

    except Exception as e:
        print(f"Error occurred: {str(e)}") 
        return jsonify({"error": str(e)}), 500

@app.route('/getCard3', methods=['GET'])
def claims_processed_count():
    try:
        today = datetime.now(timezone.utc).date()
        yesterday = today - timedelta(days=1)

        start_of_today = datetime.combine(today, datetime.min.time(), tzinfo=timezone.utc)
        end_of_today = datetime.combine(today, datetime.max.time(), tzinfo=timezone.utc)

        start_of_yesterday = datetime.combine(yesterday, datetime.min.time(), tzinfo=timezone.utc)
        end_of_yesterday = datetime.combine(yesterday, datetime.max.time(), tzinfo=timezone.utc)

        # Month start date
        month_start = today.replace(day=1)
        start_of_month = datetime.combine(month_start, datetime.min.time(), tzinfo=timezone.utc)

        # Quarter start date
        current_month = today.month
        quarter_start_month = (current_month - 1) // 3 * 3 + 1
        quarter_start_date = today.replace(month=quarter_start_month, day=1)
        start_of_quarter = datetime.combine(quarter_start_date, datetime.min.time(), tzinfo=timezone.utc)

        today_count = db.session.query(func.count(Claim.id)).filter(
            Claim.stage_date >= start_of_today,
            Claim.stage_date <= end_of_today
        ).scalar() or 0

        yesterday_count = db.session.query(func.count(Claim.id)).filter(
            Claim.stage_date >= start_of_yesterday,
            Claim.stage_date <= end_of_yesterday
        ).scalar() or 0

        month_count = db.session.query(func.count(Claim.id)).filter(
            Claim.stage_date >= start_of_month
        ).scalar() or 0

        quarter_count = db.session.query(func.count(Claim.id)).filter(
            Claim.stage_date >= start_of_quarter
        ).scalar() or 0

        response_data = {
            "today": today_count,
            "yesterday": yesterday_count,
            "month_to_date": round(month_count),
            "quarter_to_date": round(quarter_count),
        }

        return jsonify(response_data), 200

    except Exception as e:
        print(f"Error occurred: {str(e)}")  
        return jsonify({"error": str(e)}), 500

# current-month-status
@app.route('/getCard4', methods=['GET'])
def current_month_status():
    try:
        today = datetime.now(timezone.utc).date()
        month_start = today.replace(day=1)

        total_claims = db.session.query(func.count(Claim.id)).filter(
            Claim.stage_date >= month_start
        ).scalar() or 0

        sla_met_count = db.session.query(func.count(Claim.id)).filter(
            Claim.stage_date >= month_start,
            Claim.sla_met > 0 
        ).scalar() or 0

        sla_breached_count = db.session.query(func.count(Claim.id)).filter(
            Claim.stage_date >= month_start,
            Claim.sla_breached > 0 
        ).scalar() or 0

        abandoned_count = db.session.query(func.count(Claim.id)).filter(
            Claim.stage_date >= month_start,
            Claim.abandoned > 0  
        ).scalar() or 0

        response_data = {
            "total_claims": total_claims,
            "sla_met": sla_met_count,
            "sla_breached": sla_breached_count,
            "abandoned": abandoned_count,
        }

        return jsonify(response_data), 200

    except Exception as e:
        print(f"Error occurred: {str(e)}") 
        return jsonify({"error": str(e)}), 500

@app.route('/getLobCard1', methods=['GET'])
def get_active_lob_claims():
    c_lob = request.args.get('c_lob') 
    try:
        active_claims = Claim.query.filter(
            Claim.claims_pending > 0,
            Claim.c_lob == c_lob 
        ).all()

        # Calculate counts of pending and SLA breached claims
        pending_claim_count = sum(claim.claims_pending or 0 for claim in active_claims)
        sla_breached_count = sum(claim.sla_breached or 0 for claim in active_claims)

        active_claims_data = []
        for claim in active_claims:
            active_claims_data.append({
                "id": claim.id,
                "g_loss": claim.g_loss,
                "stage_name": claim.stage_name,
                "stage_date": claim.stage_date.isoformat() if claim.stage_date else '',
                "t_clm_nbr": claim.t_clm_nbr,
                "c_lob": claim.c_lob,
                "claims_pending": claim.claims_pending or 0,
                "sla_breached": claim.sla_breached or 0,
                "time_taken": claim.time_taken or 0,
                "region": claim.region,
            })

        return jsonify({
            "claim_pending": pending_claim_count,
            "sla_breached": sla_breached_count
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/getLobCard2', methods=['GET'])
def average_processing_lob_time():
    c_lob = request.args.get('c_lob')  
    try:
        today = datetime.now(timezone.utc).date()
        first_day_of_month = today.replace(day=1)

        start_of_today = datetime.combine(today, datetime.min.time(), tzinfo=timezone.utc)
        end_of_today = datetime.combine(today, datetime.max.time(), tzinfo=timezone.utc)

        # Average processing time for today
        today_avg = db.session.query(func.avg(Claim.time_taken)).filter(
            Claim.stage_date >= start_of_today,
            Claim.stage_date <= end_of_today,
            Claim.c_lob == c_lob 
        ).scalar() or 0

        # Average processing time for the current month
        month_avg = db.session.query(func.avg(Claim.time_taken)).filter(
            extract('month', Claim.stage_date) == today.month,
            extract('year', Claim.stage_date) == today.year,
            Claim.c_lob == c_lob 
        ).scalar() or 0

        lob_count = db.session.query(
            Claim.c_lob,
            func.count(Claim.id)
        ).filter(Claim.c_lob == c_lob).group_by(Claim.c_lob).all()

        region_count = db.session.query(
            Claim.region,
            func.count(Claim.id)
        ).filter(Claim.c_lob == c_lob).group_by(Claim.region).all()

        response_data = {
            "today_average": round(today_avg),
            "month_average": round(month_avg),
            "lob_average": sum(count for lob, count in lob_count),
            "region_average": sum(count for region, count in region_count)
        }

        return jsonify(response_data), 200

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/getLobCard3', methods=['GET'])
def claims_processed_lob_count():
    c_lob = request.args.get('c_lob') 
    try:
        today = datetime.now(timezone.utc).date()
        yesterday = today - timedelta(days=1)

        start_of_today = datetime.combine(today, datetime.min.time(), tzinfo=timezone.utc)
        end_of_today = datetime.combine(today, datetime.max.time(), tzinfo=timezone.utc)

        start_of_yesterday = datetime.combine(yesterday, datetime.min.time(), tzinfo=timezone.utc)
        end_of_yesterday = datetime.combine(yesterday, datetime.max.time(), tzinfo=timezone.utc)

        month_start = today.replace(day=1)
        start_of_month = datetime.combine(month_start, datetime.min.time(), tzinfo=timezone.utc)

        current_month = today.month
        quarter_start_month = (current_month - 1) // 3 * 3 + 1
        quarter_start_date = today.replace(month=quarter_start_month, day=1)
        start_of_quarter = datetime.combine(quarter_start_date, datetime.min.time(), tzinfo=timezone.utc)

        # Count claims processed today
        today_count = db.session.query(func.count(Claim.id)).filter(
            Claim.stage_date >= start_of_today,
            Claim.stage_date <= end_of_today,
            Claim.c_lob == c_lob  
        ).scalar() or 0

        # Count claims processed yesterday
        yesterday_count = db.session.query(func.count(Claim.id)).filter(
            Claim.stage_date >= start_of_yesterday,
            Claim.stage_date <= end_of_yesterday,
            Claim.c_lob == c_lob  # Filter by c_lob
        ).scalar() or 0

        month_count = db.session.query(func.count(Claim.id)).filter(
            Claim.stage_date >= start_of_month,
            Claim.c_lob == c_lob 
        ).scalar() or 0

        # Count claims processed quarter-to-date
        quarter_count = db.session.query(func.count(Claim.id)).filter(
            Claim.stage_date >= start_of_quarter,
            Claim.c_lob == c_lob
        ).scalar() or 0

        response_data = {
            "today": today_count,
            "yesterday": yesterday_count,
            "month_to_date": round(month_count),
            "quarter_to_date": round(quarter_count),
        }

        return jsonify(response_data), 200

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/getLobCard4', methods=['GET'])
def current_month_lob_status():
    c_lob = request.args.get('c_lob')  
    try:
        today = datetime.now(timezone.utc).date()
        month_start = today.replace(day=1)

        total_claims = db.session.query(func.count(Claim.id)).filter(
            Claim.stage_date >= month_start,
            Claim.c_lob == c_lob 
        ).scalar() or 0

        sla_met_count = db.session.query(func.count(Claim.id)).filter(
            Claim.stage_date >= month_start,
            Claim.sla_met > 0,
            Claim.c_lob == c_lob
        ).scalar() or 0

        sla_breached_count = db.session.query(func.count(Claim.id)).filter(
            Claim.stage_date >= month_start,
            Claim.sla_breached > 0,
            Claim.c_lob == c_lob  
        ).scalar() or 0

        abandoned_count = db.session.query(func.count(Claim.id)).filter(
            Claim.stage_date >= month_start,
            Claim.abandoned > 0,
            Claim.c_lob == c_lob  
        ).scalar() or 0

        response_data = {
            "total_claims": total_claims,
            "sla_met": sla_met_count,
            "sla_breached": sla_breached_count,
            "abandoned": abandoned_count,
        }

        return jsonify(response_data), 200

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/line-chart', methods=['GET'])
def lob_average_processing_time():
    try:
        # Get the current date
        today = datetime.now()
        # Calculate the start of the current year and the start of the current month
        start_of_current_year = today.replace(month=1, day=1)
        start_of_current_month = today.replace(day=1)

        monthwise_avg = db.session.query(
            Claim.c_lob,
            extract('year', Claim.stage_date).label('year'),
            extract('month', Claim.stage_date).label('month'),
            func.avg(Claim.time_taken).label('avg_time')
        ).filter(
            Claim.stage_date >= start_of_current_year
        ).group_by(
            Claim.c_lob,
            extract('year', Claim.stage_date),
            extract('month', Claim.stage_date)
        ).all()

        yearwise_avg = db.session.query(
            Claim.c_lob,
            extract('year', Claim.stage_date).label('year'),
            func.avg(Claim.time_taken).label('avg_time')
        ).filter(
            Claim.stage_date >= start_of_current_year
        ).group_by(
            Claim.c_lob,
            extract('year', Claim.stage_date)
        ).all()
        monthwise_avg_data = [
            {
                "lob": result.c_lob,
                "year": result.year,
                "month": result.month,
                "avg_time": result.avg_time
            } for result in monthwise_avg
        ]

        yearwise_avg_data = [
            {
                "lob": result.c_lob,
                "year": result.year,
                "avg_time": result.avg_time
            } for result in yearwise_avg
        ]

        return jsonify({
            "monthwise_average": monthwise_avg_data,
            "yearwise_average": yearwise_avg_data
        }), 200

    except Exception as e:
        print(f"Error occurred: {str(e)}")  
        return jsonify({"error": str(e)}), 500

@app.route('/column-chart', methods=['GET'])
def get_regional_average():
    results = db.session.query(
        Claim.region,
        db.func.avg(Claim.claims_processed_today).label('average_claims_processed')
    ).group_by(Claim.region).all()
    response_data = [{'region': row[0], 'average_claims_processed': row[1]} for row in results]

    return jsonify(response_data)

@app.route('/heat-chart', methods=['GET'])
def get_heatmap_data():
    stages = ["Claim Loaded", "Claim Registered", "FNOL Submitted", "Adjuster Assigned"]
    averages = [
        [5, 10, 15, 20],  
        [3, 8, 12, 18],  
        [7, 14, 20, 25],  
        [2, 5, 10, 15]  
    ]
    
    heatmap_data = {
        "stages": stages,
        "averages": averages
    }

    return jsonify(heatmap_data)

@app.route('/pie-chart', methods=['GET'])
def get_stage_wise_time():
    results = db.session.query(
        Claim.stage_name, 
        db.func.avg(Claim.time_taken).label('average_time_taken') 
    ).group_by(Claim.stage_name).all()

    response_data = [{'stage': row[0], 'average_time_taken': row[1]} for row in results]

    return jsonify(response_data)

@app.route('/lob-line-chart', methods=['GET'])
def lob_average_processing_time_clob():
    try:
        # Get the current date
        today = datetime.now()
        # Calculate the start of the current year
        start_of_current_year = today.replace(month=1, day=1)

        # Get c_lob from query parameters
        c_lob = request.args.get('c_lob')

        # Validate the input
        if not c_lob:
            return jsonify({"error": "c_lob is required"}), 400

        # Month-wise average processing time
        monthwise_avg = db.session.query(
            Claim.c_lob,
            extract('year', Claim.stage_date).label('year'),
            extract('month', Claim.stage_date).label('month'),
            func.avg(Claim.time_taken).label('avg_time')
        ).filter(
            Claim.stage_date >= start_of_current_year,
            Claim.c_lob == c_lob  # Filter by the specific c_lob
        ).group_by(
            Claim.c_lob,
            extract('year', Claim.stage_date),
            extract('month', Claim.stage_date)
        ).all()

        # Year-wise average processing time
        yearwise_avg = db.session.query(
            Claim.c_lob,
            extract('year', Claim.stage_date).label('year'),
            func.avg(Claim.time_taken).label('avg_time')
        ).filter(
            Claim.stage_date >= start_of_current_year,
            Claim.c_lob == c_lob  # Filter by the specific c_lob
        ).group_by(
            Claim.c_lob,
            extract('year', Claim.stage_date)
        ).all()

        # Prepare response data
        monthwise_avg_data = [
            {
                "lob": result.c_lob,
                "year": result.year,
                "month": result.month,
                "avg_time": result.avg_time
            } for result in monthwise_avg
        ]

        yearwise_avg_data = [
            {
                "lob": result.c_lob,
                "year": result.year,
                "avg_time": result.avg_time
            } for result in yearwise_avg
        ]

        return jsonify({
            "monthwise_average": monthwise_avg_data,
            "yearwise_average": yearwise_avg_data
        }), 200

    except Exception as e:
        print(f"Error occurred: {str(e)}") 
        return jsonify({"error": str(e)}), 500

@app.route('/lob-column-chart', methods=['GET'])
def get_regional_average_clob():
    # Get c_lob from query parameters
    c_lob = request.args.get('c_lob')

    # Validate the input
    if not c_lob:
        return jsonify({"error": "c_lob is required"}), 400

    # Query to get the average claims processed by region for the specific c_lob
    results = db.session.query(
        Claim.region,
        db.func.avg(Claim.claims_processed_today).label('average_claims_processed')
    ).filter(Claim.c_lob == c_lob).group_by(Claim.region).all()

    # Prepare the response data
    response_data = [{'region': row[0], 'average_claims_processed': row[1]} for row in results]

    return jsonify(response_data)

@app.route('/lob-heat-chart', methods=['GET'])
def get_heatmap_data_clob():
    c_lob = request.args.get('c_lob')

    if not c_lob:
        return jsonify({"error": "c_lob is required"}), 400

    stages = ["Claim Loaded", "Claim Registered", "FNOL Submitted", "Adjuster Assigned"]
    
    averages = [
        [5, 10, 15, 20],
        [3, 8, 12, 18],   
        [7, 14, 20, 25], 
        [2, 5, 10, 15]   
    ]
    
    heatmap_data = {
        "stages": stages,
        "averages": averages
    }

    return jsonify(heatmap_data)

@app.route('/lob-pie-chart', methods=['GET'])
def get_stage_wise_time_clob():
    c_lob = request.args.get('c_lob')

    if not c_lob:
        return jsonify({"error": "c_lob is required"}), 400

    results = db.session.query(
        Claim.stage_name,
        db.func.avg(Claim.time_taken).label('average_time_taken')
    ).filter(Claim.c_lob == c_lob).group_by(Claim.stage_name).all()
    response_data = [{'stage': row[0], 'average_time_taken': row[1]} for row in results]
    return jsonify(response_data)

@app.route('/category-line-chart', methods=['GET'])
def lob_average_processing_time_ctgry():
    try:
        today = datetime.now()
        start_of_current_year = today.replace(month=1, day=1)

        c_lob_ctgry = request.args.get('c_lob_ctgry')

        if not c_lob_ctgry:
            return jsonify({"error": "c_lob_ctgry is required"}), 400

        monthwise_avg = db.session.query(
            Claim.c_lob_ctgry,
            extract('year', Claim.stage_date).label('year'),
            extract('month', Claim.stage_date).label('month'),
            func.avg(Claim.time_taken).label('avg_time')
        ).filter(
            Claim.stage_date >= start_of_current_year,
            Claim.c_lob_ctgry == c_lob_ctgry  
        ).group_by(
            Claim.c_lob_ctgry,
            extract('year', Claim.stage_date),
            extract('month', Claim.stage_date)
        ).all()
        yearwise_avg = db.session.query(
            Claim.c_lob_ctgry,
            extract('year', Claim.stage_date).label('year'),
            func.avg(Claim.time_taken).label('avg_time')
        ).filter(
            Claim.stage_date >= start_of_current_year,
            Claim.c_lob_ctgry == c_lob_ctgry  
        ).group_by(
            Claim.c_lob_ctgry,
            extract('year', Claim.stage_date)
        ).all()
        monthwise_avg_data = [
            {
                "lob_ctgry": result.c_lob_ctgry,
                "year": result.year,
                "month": result.month,
                "avg_time": result.avg_time
            } for result in monthwise_avg
        ]

        yearwise_avg_data = [
            {
                "lob_ctgry": result.c_lob_ctgry,
                "year": result.year,
                "avg_time": result.avg_time
            } for result in yearwise_avg
        ]
        return jsonify({
            "monthwise_average": monthwise_avg_data,
            "yearwise_average": yearwise_avg_data
        }), 200
    except Exception as e:
        print(f"Error occurred: {str(e)}")  
        return jsonify({"error": str(e)}), 500

@app.route('/category-column-chart', methods=['GET'])
def get_regional_average_ctgry():
    c_lob_ctgry = request.args.get('c_lob_ctgry')
    if not c_lob_ctgry:
        return jsonify({"error": "c_lob_ctgry is required"}), 400
    results = db.session.query(
        Claim.region,
        db.func.avg(Claim.claims_processed_today).label('average_claims_processed')
    ).filter(Claim.c_lob_ctgry == c_lob_ctgry).group_by(Claim.region).all()
    response_data = [{'region': row[0], 'average_claims_processed': row[1]} for row in results]
    return jsonify(response_data)

@app.route('/category-heat-chart', methods=['GET'])
def get_heatmap_data_ctgry():
    c_lob_ctgry = request.args.get('c_lob_ctgry')

    if not c_lob_ctgry:
        return jsonify({"error": "c_lob_ctgry is required"}), 400

    stages = ["Claim Loaded", "Claim Registered", "FNOL Submitted", "Adjuster Assigned"]
    
    averages = [
        [5, 10, 15, 20],  
        [3, 8, 12, 18],   
        [7, 14, 20, 25],  
        [2, 5, 10, 15]   
    ]
    
    heatmap_data = {
        "stages": stages,
        "averages": averages
    }

    return jsonify(heatmap_data)

@app.route('/category-pie-chart', methods=['GET'])
def get_stage_wise_time_ctgry():
    c_lob_ctgry = request.args.get('c_lob_ctgry')
    if not c_lob_ctgry:
        return jsonify({"error": "c_lob_ctgry is required"}), 400
    results = db.session.query(
        Claim.stage_name,
        db.func.avg(Claim.time_taken).label('average_time_taken')
    ).filter(Claim.c_lob_ctgry == c_lob_ctgry).group_by(Claim.stage_name).all()
    response_data = [{'stage': row[0], 'average_time_taken': row[1]} for row in results]

    return jsonify(response_data)


# GPT-2 Text Generation Pipeline
model_name = "gpt2"
nlp_pipeline = pipeline("text-generation", model=model_name)

@app.route('/gpt-prompt', methods=['POST'])
def classify_text():
    data = request.json
    input_text = data.get('input')
    if not input_text:
        return jsonify({"error": "No input text provided"}), 400
    try:
        result = nlp_pipeline(input_text, max_length=150, num_return_sequences=1, temperature=0.7)
        return jsonify(result[0])  
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
