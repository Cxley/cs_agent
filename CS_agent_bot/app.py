from flask import Flask, request, jsonify, render_template
from memory import get_user, save_user
from agent import run_agent

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_id = data.get("user_id")
    message = data.get("message")

    user = get_user(user_id)

    # add user message to conversation history
    user["history"].append({"role": "user", "content": message})

    # run the AI agent
    reply = run_agent(user, message)

    # add assistant reply to history
    user["history"].append({"role": "assistant", "content": reply})

    save_user(user_id, user)

    return jsonify({"reply": reply})


if __name__ == "__main__":
    app.run(debug=True)