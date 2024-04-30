from flask import Flask, render_template, request, jsonify
from data import db_session
from flask_restful import Api
import sqlite3
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
api = Api(app)


def main():
    db_session.global_init("db/calls_mg.sqlite")


@app.route('/')
@app.route('/show_data', methods=['GET', 'POST'])
def show_data():
    connect = sqlite3.connect('db/calls_mg.sqlite')
    cursor = connect.cursor()

    current_date = datetime.datetime.now().date()
    current_month_start = datetime.datetime(current_date.year,
                                            current_date.month, 1).date()

    cursor.execute("SELECT name FROM persons")
    all_persons = [row[0] for row in cursor.fetchall()]

    cursor.execute(f"""
                            SELECT p.name, count(c.phoneb) AS calls_count, 
                                count(distinct c.phoneb) AS uniq, 
                            SUM(c.billsec) / 60 AS minutes
                            FROM calls c
                            INNER JOIN persons p ON c.phonea = p.phone
                            WHERE c.phoneb > 4 
                                AND DATE(c.datetime) = DATE('{current_date}')
                            GROUP BY c.phonea, p.name
                        """)
    row = cursor.fetchall()

    data1 = [{'name': name, 'calls_count': calls_count, 'uniq': uniq,
              'minutes': minutes} for
             name, calls_count, uniq, minutes in row]

    if not row:
        data1 = [{'name': name, 'calls_count': 0, 'uniq': 0, 'minutes': 0}
                 for name in all_persons]

    cursor.execute(f"""
                                WITH FilteredCalls AS (
                                    SELECT DATE(c.datetime) AS date, p.name, c.phonea, 
                                    count(c.phoneb) AS calls_count, 
                                        count(distinct c.phoneb) AS uniq, SUM(c.billsec) / 60 
                                        AS minutes
                                    FROM calls c
                                    INNER JOIN persons p ON c.phonea = p.phone
                                    WHERE c.phoneb > 4 
                                        AND DATE(c.datetime) BETWEEN 
                                        DATE('{current_month_start}') AND 
                                        DATE('{current_date}')
                                    GROUP BY date, c.phonea, p.name
                                )
                                SELECT name, SUM(calls_count) 
                                AS calls_count_per_month, 
                                    SUM(uniq) AS unic_per_month, SUM(minutes) 
                                    AS minutes_per_month
                                FROM FilteredCalls
                                GROUP BY name, phonea
                            """)
    row2 = cursor.fetchall()

    data2 = [{'name': name, 'calls_count_per_month': calls_count,
              'unic_per_month': uniq, 'minutes_per_month': minutes}
             for name, calls_count, uniq, minutes in row2]

    if not row2:
        data2 = [{'name': name, 'calls_count_per_month': 0, 'unic_per_month': 0,
                  'minutes_per_month': 0} for name in
                 all_persons]

    data1_dict = {item['name']: item for item in data1}
    data2_dict = {item['name']: item for item in data2}

    for key, value in data2_dict.items():
        if key in data1_dict:
            data1_dict[key].update(value)
        else:
            data1_dict[key] = value

    combined_data = list(data1_dict.values())

    return render_template('data_table.html',
                           data=combined_data)


@app.route('/show_more_data', methods=['GET', 'POST'])
def show_more_data():
    connect = sqlite3.connect('db/calls_mg.sqlite')
    cursor = connect.cursor()

    start = request.args.get('start', '')
    end = request.args.get('end', '')

    cursor.execute("SELECT name FROM persons")
    all_persons = [row[0] for row in cursor.fetchall()]

    cursor.execute(f"""
                            WITH FilteredCalls AS (
                                    SELECT DATE(c.datetime) AS date, p.name, c.phonea, 
                                    count(c.phoneb) AS calls_count, 
                                        count(distinct c.phoneb) AS uniq, SUM(c.billsec) / 60 
                                        AS minutes
                                    FROM calls c
                                    INNER JOIN persons p ON c.phonea = p.phone
                                    WHERE c.phoneb > 4 
                                        AND DATE(c.datetime) BETWEEN DATE('{start}')
                                         AND DATE('{end}')
                                    GROUP BY date, c.phonea, p.name
                                )
                                SELECT name, SUM(calls_count) 
                                AS calls_count_for_that_time, 
                                    SUM(uniq) AS unic_for_that_time, SUM(minutes) 
                                    AS minutes_for_that_time
                                FROM FilteredCalls
                                GROUP BY name, phonea
                        """)
    row = cursor.fetchall()

    data1 = [
        {'name': name, 'calls_count_for_that_time': calls_count_for_that_time,
         'unic_for_that_time': unic_for_that_time,
         'minutes_for_that_time': minutes_for_that_time} for
        name, calls_count_for_that_time, unic_for_that_time,
        minutes_for_that_time in row]

    if not row:
        data1 = [{'name': name, 'calls_count_for_that_time': 0,
                  'unic_for_that_time': 0, 'minutes_for_that_time': 0} for
                 name in all_persons]

    data1_dict = {item['name']: item for item in data1}

    combined_data = list(data1_dict.values())

    return render_template('data_table_2nd.html',
                           data=combined_data)


@app.route('/add_data', methods=['POST'])
def add_data():
    calls_data = request.json

    conn = sqlite3.connect('db/calls_mg.sqlite')
    cursor = conn.cursor()

    for call in calls_data:
        cursor.execute(
            "INSERT INTO calls (datetime, phonea, "
            "phoneb, direction, billsec, linkedid) VALUES (?, ?, ?, ?, ?, ?)",
            (call['datetime'], call['phonea'], call['phoneb'],
             call['direction'], call['billsec'], call['linkedid']))

    conn.commit()

    conn.close()

    return jsonify({"message": "Данные успешно добавлены"}), 200


@app.route('/change_data', methods=['POST'])
def change_data():
    data = request.get_json()
    if not data:
        return jsonify({'message': 'No input data provided'}), 400

    conn = sqlite3.connect('db/calls_mg.sqlite')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM persons WHERE id=?",
                   (data['id'],))
    user = cursor.fetchone()

    if user:
        cursor.execute("UPDATE persons SET name=?, phone=? "
                       "WHERE id=?", (data['name'], data['phone'],
                                      data['id']))
    else:
        cursor.execute("INSERT INTO persons (name, phone) "
                       "VALUES (?, ?)", (data['name'], data['phone']))

    conn.commit()
    conn.close()

    return jsonify({'message': 'User data updated or added successfully'}), 200


app.run(debug=True)

if __name__ == '__main__':
    main()
