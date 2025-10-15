from flask import Flask, request, send_file
from string import Template
import pdfkit
import io
from flask_cors import CORS
import base64

config = pdfkit.configuration(wkhtmltopdf='/usr/bin/wkhtmltopdf')
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # 2MB limit

CORS(app, resources={r"/*": {"origins": "*"}},
     allow_headers=["X-aws-ec2-metadata-token-ttl-seconds"],
     methods=["GET","POST","PUT","OPTIONS"])

with open('static/certificate.png', 'rb') as img_file:
    encoded_img = base64.b64encode(img_file.read()).decode("utf-8")
encoded_img = encoded_img.replace("\n","")

# Simple HTML template for the flyer
FLYER_TEMPLATE = """
<html>
<head>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Chewy&display=swap');

        html, body {
        height: 100%;
        margin: 0;
        padding: 0;
        position: relative;
        }
        body {
        font-family: 'Chewy', cursive, Arial, sans-serif;
        background: url("data:image/png;base64,$background_img") no-repeat center center;
        background-size: cover;
        color: #333;
        }
        .flyer {
            position: fixed;
            bottom: 150px;
            left: 0;
            right: 0;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            max-width: 650px;
            width: calc(100% - 60px);
            border-radius: 15px;
            box-shadow: 0 6px 15px rgba(214, 40, 40, 0.15);
            text-align: center;
        }
        h1 { 
            color: #b22222; 
            font-size: 36px; 
            margin-bottom: 10px;
        }
        .info { 
            font-size: 20px; 
            color: #4a1a1a; 
            margin-top: 20px;
            line-height: 1.5;
        }
        .logo {
            text-align: center;
        }
        .logo img {
            display: block;
            max-width: 100%;
            height: auto;
            margin: 0 auto;
        }
    </style>
</head>
<body>
    <div class="flyer">
    <div class="logo">$name</div>
        <div class="info">
            <p>$description</p>
            <p>Issued by: $contact</p>
        </div>
    </div>
</body>
</html>
"""


@app.route('/generate-flyer', methods=['POST','GET'])
def generate_flyer():
    name = request.form.get('name')
    description = request.form.get('description')
    contact = request.form.get('contact')
    template = Template(FLYER_TEMPLATE)

    html_out = template.substitute(
        name=name,
        description=description,
        contact=contact,
        background_img=encoded_img
    )

    pdf_bytes = pdfkit.from_string(html_out, False, options={
        'enable-local-file-access': '',
        'encoding': 'UTF-8',
        'dpi': '96',
        'enable-javascript': '',
        'javascript-delay': '1000',
        'load-error-handling': 'ignore'
    }, configuration=config)


    return send_file(
        io.BytesIO(pdf_bytes),
        download_name='cert.pdf',
        mimetype='application/pdf'
    )


@app.route('/')
def index():
    return '''
<!DOCTYPE html>
<html>
<head>
    <title>🎅 Santa ClAWS Certificate Generator🎄</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Baloo+2&display=swap');

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #fff8f8;
            color: #333;
            padding: 40px;
            max-width: 800px;
            margin: auto;
            
        }

        /* Overlay to keep text fully visible */
        body::before {
            content: "";
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background: #fff8f8;
            opacity: 0.95;
            pointer-events: none;
            z-index: -1;
        }

        h1 {
            font-family: 'Baloo 2', cursive;
            color: #b22222; /* Firebrick red */
            margin-bottom: 0;
            font-size: 2.8rem;
        }

        h2 {
            font-family: 'Baloo 2', cursive;
            color: #c0392b; /* Dark red */
            font-weight: normal;
            margin-top: 5px;
            font-size: 1.6rem;
        }

        p em {
            color: #a04040;
            font-style: normal;
            font-weight: 600;
        }

        .form-box {
            background-color: #fff0f0; /* very light red/pink */
            border: 1px solid #f5c6c3;
            padding: 30px 25px;
            border-radius: 15px;
            box-shadow: 0 6px 12px rgba(210, 40, 40, 0.15);
            position: relative;
        }

        label {
            display: flex;
            align-items: center;
            gap: 8px;
            margin-top: 20px;
            font-weight: 600;
            color: #d43f3f;
            font-size: 1.1rem;
        }


        input[type="text"],
        input[type="email"],
        textarea {
            width: 100%;
            padding: 12px;
            margin-top: 8px;
            border: 1.5px solid #d9534f;
            border-radius: 8px;
            box-sizing: border-box;
            font-size: 1rem;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            transition: border-color 0.3s ease;
        }

        input[type="text"]:focus,
        input[type="email"]:focus,
        textarea:focus {
            border-color: #a71d1d;
            outline: none;
            background-color: #ffeaea;
        }

        textarea {
            resize: vertical;
            min-height: 100px;
        }

        .submit-btn {
            margin-top: 30px;
            background-color: #d62828; /* Strong red */
            color: white;
            padding: 14px 28px;
            border: none;
            border-radius: 10px;
            font-size: 1.2rem;
            cursor: pointer;
            font-family: 'Baloo 2', cursive;
            box-shadow: 0 4px 10px rgba(214, 40, 40, 0.6);
            transition: background-color 0.3s ease;
        }

        .submit-btn:hover {
            background-color: #a71d1d; /* Darker red hover */
            box-shadow: 0 6px 14px rgba(167, 29, 29, 0.8);
        }
    </style>
</head>
<body>
<h1>🎅 Santa ClAWS Certificate Generator 🎄</h1>
    <h2>Securely Awarding Certificates to Good Cattos 🐱</h2>
    <p><em>Generate official Santa ClAWS certificates for those on the Nice List.</em></p>

    <div class="form-box">
        <form method="POST" action="/generate-flyer">
            <label for="name">Name</label>
            <input type="text" id="name" name="name" placeholder="Meow">

            <label for="description">Certificate Description</label>
            <textarea id="description" name="description" rows="4" placeholder="Describe the reason for the certificate...">Awarded for exemplary behavior this year.</textarea>

            <label for="contact">Contact Email</label>
            <input type="email" id="contact" name="contact" value="contact@santaclaws.com">

            <button type="submit" class="submit-btn">Generate Certificate PDF</button>
        </form>
    </div>
<!-- TODO: Verify the systemd service config for runtime ports (done) -->
</body>
</html>
    '''

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8000,debug=True)