# -*- coding: latin1 -*-

def user():
    return dict(form=auth())

@auth.requires_login()
def index():
    ## Creates a list of the last 5 files correctly inputed
    user = (db.processo.usuario == auth.user_id)
    myset = db(user)
    last = myset.select(db.processo.ALL, orderby=~db.processo.id, limitby=(0, 5))
    
    ## Shows a statistic of the files inputed in the month
    ## Establishing todays month 
    today_month= str(request.now)[5:7]
    mes = (db.processo.criado_em.month() == today_month)
    
    ## Establishing todays year 
    today_year= str(request.now)[0:4]
    ano = (db.processo.criado_em.year() == today_year)
    
    relatora = ((db.processo.competencia == "Relatora") & mes & ano )
    session.frelatora=db(relatora).count()
    revisora = ((db.processo.competencia == "Revisora") & mes & ano)
    session.frevisora=db(revisora).count()
    session.ftotal = session.frelatora+session.frevisora
    
    return dict(rows=last)
   


def cadastro():

    form = SQLFORM.factory(Field('processo', label=T('Numero do Processo: '), requires=IS_NOT_EMPTY()))

    if form.process().accepted:

        soup_cadastrar(form.vars.processo)

    return dict(form=form)

def soup_cadastrar(num):
    import tj
    processo = tj.get_page(num)
    if len(processo)== 4:

        session.processo_one = processo[0].decode('latin1')
        session.classe_one = processo[1].decode('latin1')
        session.processo_two = processo[2].decode('latin1')
        session.classe_two = processo[3].decode('latin1')

        redirect(URL('escolhe_processo'))

    else:
       session.reu = processo[0].decode("latin1", "ignore")
       session.classe = processo[1].decode("latin1", "ignore")
       session.numero = processo[2]
       session.crime = processo[3].decode("latin1", "ignore")
       session.competencia = processo[4]
       redirect(URL('cadastro_final'))

    return 0



def cadastro_final():

    ##creating the submission form and hidding the date and user, which are filled in automatically
    db.processo.criado_em.writable = False
    db.processo.criado_em.readable = False
    db.processo.usuario.writable = False
    db.processo.usuario.readable = False
    form = SQLFORM(db.processo)
    ##pre-populating the form with the info obtained through get_page()
    form.vars.classe = session.classe.encode("utf8")
    form.vars.reu = session.reu.encode("utf8")
    form.vars.numero = session.numero
    form.vars.competencia = session.competencia.encode("utf8")
    form.vars.crime = session.crime.encode("utf8")

    if form.process().accepted:
       session.flash = 'form accepted'
       redirect(URL('index'))

    return dict(form=form)

def pesquisa():
    form = SQLFORM.factory(Field('reu'),
    Field('numero'),
    Field('competencia'),
    Field('Data_inicial', 'date'),
    Field('Data_final', 'date', default = request.now))

    if form.process().accepted:

        if form.vars.numero!="":
            numero = db.processo.numero.contains(form.vars.numero)
            query = db(numero)
            session.rows = query.select()
            redirect(URL('result'))

        elif form.vars.reu != "":
            reu = db.processo.reu.contains(form.vars.reu)
            query = db(reu)
            session.rows = query.select()
            redirect(URL('result'))


        elif form.vars.competencia != "":
            competencia = (db.processo.competencia == form.vars.competencia)
            query = db(competencia)
            session.rows = query.select()
            redirect(URL('result'))


        elif (form.vars.Data_inicial!="") or (form.vars.Data_final!=request.now):
            import datetime
            from datetime import date
            delta = datetime.timedelta(days=1)
            session.inicial = form.vars.Data_inicial or (request.now-(60*delta))
            session.final = form.vars.Data_final or request.now
            data = (db.processo.criado_em >= session.inicial-delta) & (db.processo.criado_em <= session.final+delta)
            query = db(data)
            session.rows = query.select()
            redirect(URL('result'))

    return dict(form=form)

def result():
    return dict(rows=session.rows)

def escolhe_processo():
    form1 = SQLFORM.factory(Field('classe', default = session.classe_one.encode("utf8"), writable=False,))


    form2 = SQLFORM.factory(Field('classe', default = session.classe_two.encode("utf8"), writable=False ))


    if form1.process(formname='form_one').accepted:
        #response.flash = session.processo_one.encode("utf8")
        soup_cadastrar(session.processo_one)
    if form2.process(formname='form_two').accepted:
        #response.flash = session.processo_two.encode("utf8")
        soup_cadastrar(session.processo_two)

    return dict(form1=form1, form2=form2)
    
    
def estatistica():
    
    ## Establishing todays month 
    month_today= str(request.now)[5:7]
    
    ## Establishing todays year 
    today_year= str(request.now)[0:4]
    ano = (db.processo.criado_em.year() == today_year)
    
    for each in range (4, -1, -1):
        mes_pesquisa = (db.processo.criado_em.month() == (month_today-each))
        relatora = ((db.processo.competencia == "Relatora") & mes_pesquisa & ano)
        session.frelatora_each=db(relatora).count()
        revisora = ((db.processo.competencia == "Revisora") & mes_pesquisa & ano)
        session.frevisora_each=db(revisora).count()
        session.ftotal_each = session.frelatora+session.frevisora
    


    return dict()
