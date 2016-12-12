"""
Flask Documentation:     http://flask.pocoo.org/docs/
Jinja2 Documentation:    http://jinja.pocoo.org/2/documentation/
Werkzeug Documentation:  http://werkzeug.pocoo.org/documentation/

This file creates your application.
"""

import os, sys
from flask import *
from subprocess import call
from nltk import download
import RapGenerator.RapLineGenerator

app = Flask(__name__)
sys.path.append('/RapGenerator')

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'this_should_be_configured')


###
# Routing for your application.
###

def initialize_server():
    download('cmudict')
    download('averaged_perceptron_tagger')
    download('universal_tagset')
    call('git clone https://github.com/emilmont/pyStatParser.git ../pyStatParser', shell=True)
    call('python ../pyStatParser/setup.py install --user', shell=True)
    call('python ../pyStatParser/setup.py build', shell=True)
    rlg = RapGenerator.RapLineGenerator()
    rlg.readAll()
    call('rm -rf ../pyStatParser', shell=True)
    return rlg

#rlg = initialize_server()

@app.route("/result", methods=["GET", "POST"])
def result_route():
    if request.method == "POST":
        line = str(request.form['starter'])
        num_verses = int(request.form['verse_no'])
        generated_verse = "<title>S.W.A.G.G.E.R. Online Demo Results</title>"
        if len(line) == 0:
            generated_verse += 'Initial sentence: <b>real gs move in silence like lasagna</b><br /><br /><i>'
            generated_verse += '<br />'.join(rlg.generateVerse(numVerses=num_verses))
        else:
            generated_verse += 'Initial sentence: <b>' + line + '</b><br /><br /><i>'
            generated_verse += '<br />'.join(rlg.generateVerse(line, numVerses=num_verses))
        generated_verse += "</i><br /><br />Make a new phrase <a href='/'>here!</a>"

        return generated_verse

    else:
        return redirect(url_for('homepage_route'))

@app.route("/", methods=["GET", "POST"])
def homepage_route():

    initial_form = """<title>S.W.A.G.G.E.R. Online Demo</title>
    <h1>S.W.A.G.G.E.R. Online Demo</h1>
    <p>Rap is unique among music genres for its emphasis on expression through complex and meaningful lyrics. We design a system that aims to generate interesting and novel rap lyrics using a corpus of rap lyrics from popular rap artists. The system we present is based on n-gram models and probabilistic context-free grammars.</p>
    <p>Enter a sentence containing at least three words to start out with (or leave blank for a random starter):</p>
    <form action="/result" method="POST">
        <textarea name="starter" style="width:100%; font-size:1.2em;"></textarea>
        <p>Enter a number of verses you would like to produce (each takes about 10 seconds):</p>
        <select name="verse_no">
            <option value="1">1</option>
            <option value="2">2</option>
            <option value="3">3</option>
            <option value="4">4</option>
        </select><br /><br />
        <input type="submit" value="Enter sentence">
    </form>
    <br />
    <small>All work by <a href="http://umich.edu/~bradmath">Brady Mathieson</a>, <a href="mailto:nimesham@umich.edu">Nimesha Muthya</a>, <a href="http://psturmfels.github.io">Pascal Sturmfels</a>, and <a href="mailto:rosawu@umich.edu">Rosa Wu</a>.</small>
    """
    return initial_form
    
if __name__ == '__main__':
    print "Server initialized, booting up..."
    app.run(debug=True)