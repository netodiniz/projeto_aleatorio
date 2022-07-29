
import os
from flask import Flask, render_template, redirect, request, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import date, datetime
from apscheduler.schedulers.background import BackgroundScheduler


from flask_session import Session
from python_exec import buscar_registros, send_mail, create_sched, start_sched, edita_contrato
from functools import partial

#
#
#
l_sched = []
sc_conts = []

def create_app():

    #Função para criar os enviadores de email
    #

    def update_active():
        for cont in Contrato.query.all():
            if (cont.dataf - datetime.today()).days >= 0:
                cont.isActive = "Ativo"
            else:
                cont.isActive = "Inativo"
        db.session.commit()

    def update_scheds():
        global l_sched
        global sc_conts
        for cont in Contrato.query.all():
            tw = (cont.dataf - datetime.today()).days
            if not cont.id in sc_conts:
                if (tw < 15):
                    l_sched.append(create_sched(3, partial(send_mail, Email, cont.dep, cont.nome_cont, cont.resumo, cont.num_cont, cont.dataf)))
                    sc_conts.append(cont.id)    
                    continue
                
                if (tw < 30):
                    l_sched.append(create_sched(12, partial(send_mail, Email, cont.dep, cont.nome_cont, cont.resumo, cont.num_cont, cont.dataf)))
                    sc_conts.append(cont.id)
                    continue

                if (tw < 45):
                    l_sched.append(create_sched(24, partial(send_mail, Email, cont.dep, cont.nome_cont, cont.resumo, cont.num_cont, cont.dataf)))
                    sc_conts.append(cont.id)
                    continue
        start_sched(l_sched)
    #
    # Configuraçoes iniciais da aplicaçao
    #

    ## Configura agendador de tarefas
    #
    scheduler = BackgroundScheduler()
    scheduler.add_job(update_scheds, 'interval', seconds=5, id="update_s")
    scheduler.add_job(update_active, 'interval', seconds=10, id="update_a")
    scheduler.start()

    ##


    app = Flask(__name__)

    app.config["SESSION_PERMANENT"] = False
    app.config["SESSION_TYPE"] = "filesystem"
    Session(app)

    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] =\
        'sqlite:///' + os.path.join(basedir, 'database.db')

    db = SQLAlchemy(app)
    
    app.config['SECRET_KEY'] = "abc123433"
        
    class Email(db.Model):
        id = db.Column(db.Integer, primary_key=True, nullable=False)
        email = db.Column(db.String(120), nullable=False)
        chapa = db.Column(db.Integer, nullable=False)
        dep = db.Column(db.String(120), nullable=False)
        admin = db.Column(db.Boolean, default=False, nullable=False)


    class Contrato(db.Model):
        id = db.Column(db.Integer, primary_key=True, nullable=False)
        resumo = db.Column(db.String(200), nullable=False)
        datai = db.Column(db.DateTime, nullable=False)
        dataf = db.Column(db.DateTime, nullable=False)
        valor = db.Column(db.Float, nullable=False)
        nome_cont = db.Column(db.String(120), nullable=False)
        nome = db.Column(db.String(120), nullable=False)
        num_cont = db.Column(db.Integer, nullable=False)
        isActive = db.Column(db.String(120), nullable=True)
        dep = db.Column(db.String(120), nullable=False)

    db.create_all()

    #
    # Rotas da aplicação
    #

    @app.route("/", methods= ["GET", "POST"])
    def index():
        if request.method == "POST":
            form = request.form
            user = Email.query.filter_by(chapa=form["chapa"]).first()
            if user:
                session["user"] = user.dep
                session["chapa"] = user.chapa
                if user.admin:
                    return redirect("/admin")
                return redirect("/cadastro")
            else:
                user = Email(email=form["email"], chapa=form["chapa"], dep=form["dep"])
                db.session.add(user)
                db.session.commit()
                session["user"] = user.dep
                return redirect("/cadastro")
        else:    
            return render_template("index.html")

    @app.route("/cadastro", methods=["GET", "POST"])
    def cadastro():
        if request.method == "POST":
            form = request.form

            return redirect(url_for("create", nome=form["nome"],
            nome_cont=form["nome_cont"],
            valor=form["valor"],
            datai=form["datai"],
            dataf=form["dataf"],
            resumo=form["resumo"],
            num_cont=form["num_cont"],
            dep=form["dep"]))

        return render_template("tela_cadastro.html", dep=Email.query.filter_by(dep=session["user"]).first().dep)

    @app.route("/contrats", methods=["GET", "POST"])
    def contratos():
        if request.method == "POST":
            form = request.form
            return render_template("tela_contratos.html", titulo="Buscar Contrato", placeh="Numero do Contrato", funcao="Buscar", dep=Email.query.filter_by(dep=session["user"]).first().dep, conts=buscar_registros(form["inp"], Contrato.query.filter_by(dep=session["user"])))
        return render_template("tela_contratos.html", titulo="Buscar Contrato", funcao="Buscar", placeh="Numero do Contrato", dep=Email.query.filter_by(dep=session["user"]).first().dep,conts=Contrato.query.filter_by(dep=session["user"]))



    @app.route("/create/<nome>/<nome_cont>/<valor>/<datai>/<dataf>/<resumo>/<num_cont>/<dep>")
    def create(nome, nome_cont, valor, datai, dataf, resumo, num_cont, dep):
        di = datai.split("-")
        df = dataf.split("-")
        di = date(int(di[0]), int(di[1]), int(di[2]))
        df = date(int(df[0]), int(df[1]) ,int(df[2]))

        contrato = Contrato(resumo=resumo, nome=nome, valor=valor,nome_cont=nome_cont, datai=di, dataf=df, num_cont=num_cont, dep=dep, isActive="Ativo")
        db.session.add(contrato)
        db.session.commit()
        return redirect("/contrats")

    @app.route("/remove", methods=["GET", "POST"])
    def remove():
        if request.method == "POST":
            form = request.form
            contrato = Contrato.query.filter_by(id=form["id"]).first()
            db.session.delete(contrato)
            db.session.commit()
        return render_template("excluir.html", dep=Email.query.filter_by(dep=session["user"]).first().dep, conts=Contrato.query.filter_by(dep=session["user"]))
    
    @app.route("/editar", methods=["GET", "POST"])
    def editar():
        if request.method == "POST":
            form = request.form
            if len(list(form.values())) == 1:
                if form["inp"]:
                    return render_template("editar.html", titulo="Buscar Contrato", placeh="Numero do Contrato", funcao="Buscar", dep=Email.query.filter_by(dep=session["user"]).first().dep, conts=buscar_registros(form["inp"], Contrato.query.filter_by(dep=session["user"])))
                else:
                    return render_template("editar.html", titulo="Buscar Contrato", placeh="Numero do Contrato", funcao="Buscar", dep=Email.query.filter_by(dep=session["user"]).first().dep, conts=Contrato.query.filter_by(dep=session["user"]))

            elif form["id"]:
                cont = Contrato.query.filter_by(id=form["id"]).first()
                cont = edita_contrato(cont, form)
                db.session.commit()
            else:
                return render_template("editar.html", titulo="Buscar Contrato", placeh="Numero do Contrato", funcao="Buscar", dep=Email.query.filter_by(dep=session["user"]).first().dep, conts=Contrato.query.filter_by(dep=session["user"]))
        return render_template("editar.html", titulo="Buscar Contrato", placeh="Numero do Contrato", funcao="Buscar", dep=Email.query.filter_by(dep=session["user"]).first().dep, conts=Contrato.query.filter_by(dep=session["user"]))
    

    #
    # Rotas do admin
    #
    @app.route("/admin", methods=["GET", "POST"])
    def admin():
        user = Email.query.filter_by(chapa=session["chapa"]).first()
        if user:
            if user.admin:
                return render_template("admin/administrador.html", dep=Email.query.filter_by(dep=session["user"]).first().dep)    
        return redirect("/")


    @app.route("/admin-users", methods=["GET", "POST"])
    def edit_users():
        user = Email.query.filter_by(chapa=session["chapa"]).first()
        if user:
            if user.admin:
                if request.method == "POST":
                    form = request.form
                    if form["id"]:
                        user = Email.query.filter_by(id=form["id"])
                        for data in form.items():
                            if data[1]:
                                if data[0] == 'email':
                                    user.email = data[1]

                                if data[0] == "chapa":
                                    user.chapa = data[1]

                                if data[0] == "dep":
                                    user.dep = data[1]

                                if data[0] == "admin":
                                    user.admin = data[1]
                        db.session.commit() 
            else:
                return redirect("/")
        return render_template("admin/admin-users.html", dep=Email.query.filter_by(dep=session["user"]).first().dep, users=Email.query.all())

    @app.route("/admin-excluir", methods=["GET", "POST"])
    def admin_excluir():
        user = Email.query.filter_by(chapa=session["chapa"]).first()
        if user:
            if user.admin:
                if request.method == "POST":
                    form = request.form
                    contrato = Contrato.query.filter_by(id=form["id"]).first()
                    db.session.delete(contrato)
                    db.session.commit()
                return render_template("admin/admin-excluir.html", dep=Email.query.filter_by(dep=session["user"]).first().dep,conts=Contrato.query.all())
        return redirect("/")

    @app.route("/admin-editar", methods=["GET", "POST"])
    def admin_editar():
        user = Email.query.filter_by(chapa=session["chapa"]).first()
        if user:
            if user.admin:
                if request.method == "POST":
                    form = request.form
                    if len(list(form.values())) == 1:
                        if form["inp"]:
                            return render_template("admin/admin-editar.html", titulo="Buscar Contrato", placeh="Numero do Contrato", funcao="Buscar", dep=Email.query.filter_by(dep=session["user"]).first().dep, conts=buscar_registros(form["inp"], Contrato.query.all()))
                        else:
                            return render_template("admin/admin-editar.html", titulo="Buscar Contrato", placeh="Numero do Contrato", funcao="Buscar", dep=Email.query.filter_by(dep=session["user"]).first().dep, conts=Contrato.query.all())

                    elif form["id"]:
                        cont = Contrato.query.filter_by(id=form["id "]).first()
                        cont = edita_contrato(cont, form)
                        db.session.commit()
                    else:
                        return render_template("admin/admin-editar.html", titulo="Buscar Contrato", placeh="Numero do Contrato", funcao="Buscar", dep=Email.query.filter_by(dep=session["user"]).first().dep, conts=Contrato.query.all())
                return render_template("admin/admin-editar.html", titulo="Buscar Contrato", placeh="Numero do Contrato", funcao="Buscar", dep=Email.query.filter_by(dep=session["user"]).first().dep,conts=Contrato.query.all())
        return redirect("/")

    return app
