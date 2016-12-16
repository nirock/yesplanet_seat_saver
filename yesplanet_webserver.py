from flask import Flask, session, redirect, url_for, escape, request

app = Flask(__name__)

@app.route('/')
def index():
    if 'username' in session:
        return 'Logged in as %s' % escape(session['username']) + '''
	        <form action="save_seats" method="post">
	            <p><input type=text name=tickets_url></p>
	            <p><input type=text name=number_of_tickets></p>
	            <p><input type=submit value=Save My Seats></p>
	        </form>
	    '''
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['username'] = request.form['username']
        return redirect(url_for('index'))
    return '''
        <form action="" method="post">
            <p><input type=text name=username></p>
            <p><input type=submit value=Login></p>
        </form>
    '''

@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/save_seats')
def save_seats():
	if request.method == 'POST':
		with YesplanetSeatSaver(tickets_url) as yss:
			yss.step0()
            show_page(yss.get_rbzid_page())
            rbzid = raw_input("Please enter rbzid (the output from pop-uped page): ")
            yss.step0_5(rbzid)
            yss.step1()
            yss.step2()
            number_of_tickets = raw_input(r"Please enter number of tickets: ")
            yss.step3(number_of_tickets)
            yss.step4()
            show_page(yss.get_seat_selector_page())
            seat_selection = raw_input(r"Please enter your seat selection: ")
            catch = 1
            while True:
                if (yss.step5(seat_selection) is True):
                    print "Saved seats successfuly"
                    catch = 0
                if catch == 1:
                    sleeping_time = 5
                else:
                    sleeping_time = 60 + random.randint(10,50)
                print "Sleeping for a %d seconds" % (sleeping_time)
                time.sleep(sleeping_time)
	return '''
        <form action="" method="post">
            <p><input type=text name=username>
            <p><input type=submit value=Login>
        </form>
    '''


# set the secret key.  keep this really secret:
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
app.run(debug=True)