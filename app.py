from flask import Flask, render_template, request, redirect, url_for
import csv

app = Flask(__name__)

# Sample Passenger DB with B-Tree Node simulation
passengers = [
    {"id": 101, "name": "Rahul", "class": "Economy", "set": "E"},
    {"id": 102, "name": "Sita", "class": "Business", "set": "B"},
    {"id": 103, "name": "Kiran", "class": "FirstClass", "set": "F"}
]

def get_safe_limit():
    total_bookings = 0
    total_no_shows = 0
    try:
        with open('historical_data.csv', mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                total_bookings += 1
                if row['show_status'].strip().lower() == 'no':
                    total_no_shows += 1
        
        no_show_rate = (total_no_shows / total_bookings) if total_bookings > 0 else 0.10
        capacity = 100
        safe_limit = capacity + int(capacity * no_show_rate * 0.8)
        return safe_limit, round(no_show_rate * 100, 2), total_bookings, total_no_shows
    except FileNotFoundError:
        return 105, 10.0, 10, 1

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    safe_limit, no_show_rate, total_b, total_ns = get_safe_limit()
    error_msg = None
    
    if request.method == 'POST':
        p_name = request.form.get('passenger_name')
        p_class = request.form.get('fare_class')
        
        if len(passengers) < safe_limit:
            new_id = 101 + len(passengers)
            set_code = "E" if p_class == "Economy" else ("B" if p_class == "Business" else "F")
            passengers.append({"id": new_id, "name": p_name, "class": p_class, "set": set_code})
            return redirect(url_for('dashboard'))
        else:
            error_msg = "Overbooking Limit Reached! Cannot add passenger."

    # DMGT Sets Grouping
    economy_set = [p['name'] for p in passengers if p['class'] == 'Economy']
    business_set = [p['name'] for p in passengers if p['class'] == 'Business']
    first_set = [p['name'] for p in passengers if p['class'] == 'FirstClass']

    return render_template('dashboard.html', 
                           passengers=passengers, 
                           limit=safe_limit, 
                           rate=no_show_rate, 
                           count=len(passengers), 
                           total_b=total_b,
                           total_ns=total_ns,
                           e_set=economy_set,
                           b_set=business_set,
                           f_set=first_set,
                           error=error_msg)

if __name__ == '__main__':
    app.run(debug=True)