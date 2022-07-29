# Sistestema de alerta de renovação de contratos

Um sistema simples feito no estágio para disparar mensagens perssonalizadas nos email listados por cada departamento no banco de dados.
Sistema feito em python, com flask no backend, e html/css no frontend.

Como rodar o projeto:

1 - git clone [url do repositorio]
2 - cd alerta_contratos
2 - pip install -r requirements.txt
3 - flask db migrate
4 - flask db upgrade
5 - flask run
