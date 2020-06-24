#importing access key and secret key from config
import config
import csv

from flask import (
	Flask, 
	jsonify,
	request,
	render_template,
	Response,
)

import pandas as pd

from functions import (
    check_present,
    append_data,
    upload_as_list,
    write_to_static,
    remove_from_static,
    load_static_csv,
    webshrinker_categories_v3,
    site_search,
    update_cats,
    add_static_cats,
)

access_key = config.access_key
secret_key = config.secret_key

app = Flask(__name__)

# i load wl 3x, feel like i shouldn't?
@app.route('/')
def home():
    return render_template("home.html")

@app.route('/', methods=['POST'])
def get_context():
    wl_list = load_static_csv()
    text = request.form['text']
    wl_check = text in wl_list
    text = bytes(text, 'utf-8')
    result = site_search(access_key, secret_key, text)
    if 'API_Error' in result:
        return render_template("home.html", fail=True, error_msg = result)
    else:
        # cats = result["data"][0]["categories"]
        # site = result["data"][0]["url"]
        # update_cats(cats, site)
        site_cat_list = add_static_cats(result)
        cats = site_cat_list[0]
        site = site_cat_list[1]
        return render_template("home.html", cats=cats, site=site, wl_valid = wl_check)

"""
categories
categoryId | url

urls
url
"""

@app.route('/whitelist')
def whitelist():
    wl_list = load_static_csv()
    return render_template("whitelist.html", wl = wl_list)

@app.route("/submit", methods=["GET", "POST"])
def submit():
    if request.method == "GET":
        return redirect(url_for('whitelist'))
    elif request.method == "POST":
        try:
            user_url = str(request.form['wlsite'])
        except:
            user_url = None
        try:
            user_url_rem = str(request.form['remwlsite'])
        except:
            user_url_rem = None
        if user_url is not None:
            if check_present(user_url) == "New":
                status = "has been added"
            else:
                status = "is already on the whitelist!"
            write_to_static(user_url)
            wl_list = load_static_csv()
        else:
            status = remove_from_static(user_url_rem)
            wl_list = load_static_csv()
    return render_template("thanks.html", user_url = user_url, user_url_rem = user_url_rem, status = status)


@app.route('/bulk', methods=['GET','POST'])
def bulkuploads():
    if request.method == "GET":
        return render_template("bulk.html")
    elif request.method == 'POST':
        #i feel like this is dumb, i'm not sure how to load the appropriate file when there are 2 on 1 page
        # setting the variable throws an error 
        try:
            wl_file = request.files['wl_upload']
        except:
            wl_file = None
        try:
            append_file = request.files['append_upload']
        except:
            append_file = None
        if append_file is not None:
            #i've beena kinda all over the place with the CSV/List/Dataframes, is there a best practice? 
            updated = append_data(upload_as_list(append_file))
            updated = updated.to_csv(index=False)
            return Response(
                updated, 
                mimetype="application/json",
                headers={"Content-Disposition": # to download the file
                                            f"attachment;filename=file.csv"})
        else:
            listver = upload_as_list(wl_file)
            for each in listver:
                write_to_static(each)
    return render_template("thanks.html", user_url="Your File", status = "has been appended to the whitelist")
    # I want to name this the filename, how could i pass that in?

@app.route('/about')
def about():
    return render_template("about.html")




if __name__ == '__main__':
    app.run(debug=True)