import os
from datetime import datetime

from flask import Flask, abort, flash, redirect, render_template, request, session, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "demo-only-change-before-production")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///loantrack_demo.db").replace("postgres://", "postgresql://", 1)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

STAGES = ["Application received", "Documents verified", "Credit assessment", "Decision", "Funds disbursed"]


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    display_name = db.Column(db.String(120), nullable=False)
    application = db.relationship("LoanApplication", backref="customer", uselist=False)


class LoanApplication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reference = db.Column(db.String(30), unique=True, nullable=False, index=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    product = db.Column(db.String(120), nullable=False)
    requested_amount = db.Column(db.Integer, nullable=False)
    stage_index = db.Column(db.Integer, nullable=False, default=0)
    next_action = db.Column(db.Text, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    history = db.relationship("StatusEvent", backref="application", lazy=True, cascade="all, delete-orphan")


class StatusEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey("loan_application.id"), nullable=False)
    stage_index = db.Column(db.Integer, nullable=False)
    message = db.Column(db.String(240), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    changed_by = db.Column(db.String(120), nullable=False)


def seed_demo_data():
    if User.query.first():
        return
    customer = User(username="LT-260912-041", password_hash=generate_password_hash("2468"), role="customer", display_name="Mary Wanjiku")
    customer_two = User(username="LT-260911-018", password_hash=generate_password_hash("1357"), role="customer", display_name="James Otieno")
    manager = User(username="manager.demo", password_hash=generate_password_hash("Manager2026!"), role="manager", display_name="Demo Branch Manager")
    db.session.add_all([customer, customer_two, manager])
    db.session.flush()
    first = LoanApplication(reference="LT-260912-041", customer=customer, product="Business expansion loan", requested_amount=250000, stage_index=2, next_action="No action is required. A decision update is expected by 16 September 2026.")
    second = LoanApplication(reference="LT-260911-018", customer=customer_two, product="Asset finance loan", requested_amount=480000, stage_index=1, next_action="Please bring the requested proof of income to the branch or upload it through the approved channel.")
    db.session.add_all([first, second])
    db.session.flush()
    db.session.add_all([
        StatusEvent(application=first, stage_index=0, message="Application received.", changed_by="System"),
        StatusEvent(application=first, stage_index=1, message="Documents passed initial checks.", changed_by="Demo Branch Manager"),
        StatusEvent(application=first, stage_index=2, message="Credit assessment is in progress.", changed_by="Demo Branch Manager"),
        StatusEvent(application=second, stage_index=0, message="Application received.", changed_by="System"),
        StatusEvent(application=second, stage_index=1, message="Documents are being checked.", changed_by="Demo Branch Manager"),
    ])
    db.session.commit()


def current_user():
    if not session.get("user_id"):
        return None
    return db.session.get(User, session["user_id"])


def require_role(role):
    user = current_user()
    if not user or user.role != role:
        abort(403)
    return user


@app.context_processor
def utility_processor():
    return {"stages": STAGES, "current_user": current_user}


@app.get("/")
def index():
    user = current_user()
    if user:
        return redirect(url_for("manager_dashboard" if user.role == "manager" else "customer_dashboard"))
    return render_template("login.html")


@app.post("/login")
def login():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")
    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password_hash, password):
        flash("The demo sign-in details do not match. Please try again.", "error")
        return redirect(url_for("index"))
    session.clear()
    session["user_id"] = user.id
    return redirect(url_for("manager_dashboard" if user.role == "manager" else "customer_dashboard"))


@app.post("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.get("/customer")
def customer_dashboard():
    user = require_role("customer")
    return render_template("customer.html", application=user.application)


@app.get("/manager")
def manager_dashboard():
    require_role("manager")
    applications = LoanApplication.query.order_by(LoanApplication.updated_at.desc()).all()
    selected = request.args.get("application", type=int)
    active = db.session.get(LoanApplication, selected) if selected else applications[0]
    return render_template("manager.html", applications=applications, active=active)


@app.post("/manager/application/<int:application_id>")
def update_application(application_id):
    manager = require_role("manager")
    application = db.get_or_404(LoanApplication, application_id)
    try:
        new_stage = int(request.form.get("stage_index"))
        if new_stage not in range(len(STAGES)):
            raise ValueError
    except (TypeError, ValueError):
        abort(400)
    note = request.form.get("message", "").strip()[:240]
    action = request.form.get("next_action", "").strip()[:500]
    application.stage_index = new_stage
    application.next_action = action or application.next_action
    db.session.add(StatusEvent(application=application, stage_index=new_stage, message=note or f"Status changed to {STAGES[new_stage]}.", changed_by=manager.display_name))
    db.session.commit()
    flash("Demo status updated. Sign in as the customer to see the change.", "success")
    return redirect(url_for("manager_dashboard", application=application.id))


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


with app.app_context():
    db.create_all()
    seed_demo_data()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=True)
