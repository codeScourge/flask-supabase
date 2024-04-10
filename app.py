import dotenv
dotenv.load_dotenv()


from flask import Flask, request, redirect, current_app, render_template
from base import supabase_client
from functools import wraps


# --- setup ---
app = Flask(__name__)
log = lambda msg: current_app.logger.info(msg)
app.secret_key = "fjdskhfadsincskafhnachydföoieszdrwiuh"


# --- decorators ---
def login_required(func):
    @wraps(func)
    def decorated_func(*args, **kwargs):

        # Try to retrieve use from SESSION
        try:
            user = supabase_client.auth.get_user()

        except Exception as e:
            user = None

        if user is None:
            return redirect("/authenticate")
        

        return func(*args, **kwargs)
        
    return decorated_func


# --- HTML routes ---
@app.get("/")
def landingRoute():
    return render_template("index.html")

@login_required
@app.get("/home")
def homeRoute():
    user = supabase_client.auth.get_user()
    return render_template("home.html")

# --- auth routes ---
@app.get("/authenticate")
def signupRoute():
    callback = f"{request.host_url}callback"
    resp = supabase_client.auth.sign_in_with_oauth(
        {
            "provider": "github",
            "options": {"redirect_to": callback},
        }
    )
    return redirect(resp.url)


@app.get("/callback")
def callbackRoute():
    code = request.args.get("code")

    # info_log("####")
    # info_log(request.args.get("error"))
    # info_log(request.args.get("error_description"))
    # info_log(request.args.get("error_uri"))
    # info_log("####")
    

    # We exchange the code for a JWT token and save it in storage
    if code:
        try:
            res = supabase_client.auth.exchange_code_for_session({"auth_code": code})
            return redirect("/home")
        
        except Exception as e:
            current_app.logger.error(e)


    return redirect("/")


@app.get("/logout")
def logoutRoute():
    supabase_client.auth.sign_out()
    return redirect("/")


# --- main ---
if __name__ == "__main__":
    app.run(debug=True, port=8080)