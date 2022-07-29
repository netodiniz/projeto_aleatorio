
from emailmsg import m_msg

import smtplib

from datetime import date, datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from apscheduler.schedulers.background import BackgroundScheduler

#
# Funçoes auxiliares
#

def create_sched(hours, job):   
    scheduler = BackgroundScheduler(job_defaults={'max_instances': 200})
    scheduler.add_job(job, 'interval', hours=hours, id="mailjob")
    return scheduler


def start_sched(sched_list):
    for s in sched_list:
        if not s.state:
            s.start()

def buscar_registros(element, contratos):
    contratos_encontrados = []
    for c in contratos:
        if element in str(c.num_cont):
            contratos_encontrados.append(c)
    return contratos_encontrados

def send_mail(mails_db, dep, nome, resumo, num, dataf):
    print("enviei")
    mail_list = mails_db.query.filter_by(dep=dep).all()
    for m in mail_list:
        server = smtplib.SMTP('smtp.gmail.com',587)
        email_site_amcel = 'site.amcel@amcel.com.br'
            
            #Senha do email
        password = "@S3nhaS3nha@"

        email_msg = MIMEMultipart()

        email_msg["From"] = email_site_amcel
        email_msg["To"] = m.email
        email_msg["Subject"] = f"Alerta de contrato, Nome: {nome}"
        email_msg.attach(MIMEText(m_msg.substitute(nome=nome, numero=num, dias=(dataf - datetime.today()).days, resumo=resumo), "html"))

        server.ehlo()
        server.starttls()
        server.login(email_site_amcel, password)
        server.sendmail(email_msg['From'], email_msg['To'], email_msg.as_string())
        server.quit()

def edita_contrato(cont, form):
    for data in form.items():
        if data[1]:
            if data[0] == 'resumo':
                cont.resumo = data[1]

            if data[0] == "datai":
                di = data[1].split("/")
                cont.datai = date(int(di[2]), int(di[1]), int(di[0]))

            if data[0] == "dataf":
                df = data[1].split("/")
                cont.dataf = date(int(df[2]), int(df[1]) ,int(df[0]))

            if data[0] == "valor":
                cont.valor = data[1]

            if data[0] == "nome_cont":
                cont.nome_cont = data[1]

            if data[0] == "nome":
                cont.nome = data[1]

            if data[0] == "num_cont":
                cont.num_cont = data[1]
    return cont