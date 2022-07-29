from string import Template

m_msg = Template("""
<body style="background: #9bddc5;">
    <div style="border: 3px solid #003503; background-color: azure; padding: 20px;">
        
        <div>       
            <p style="color: black;">
                
                <h1 style="color: black;">Vencimento do contrato: $nome</h1><br>
                <p style="color: black; font-size: 18px;">
                    Numero do contrato: $numero
                </p>
            </p>
        </div>
        <div>
            <p style="color: black; font-size: 18px;">
                Atenção o seu contrato $nome, esta prestes a vencer em $dias dias, por favor regularize.<br>
            </p>
            <p style="color: black; font-size: 18px;">
                Resumo: $resumo
            </p>
        </div>
    </div>
</body>
""")