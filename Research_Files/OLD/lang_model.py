import vertexai
from vertexai.language_models import TextGenerationModel
# db stuff
import os
import psycopg2
from psycopg2 import sql, errors
from dotenv import load_dotenv
import json

# save the data on the alert table
def db_alertdata_write(conn, alertID, data):
    print("Start alert data added to the table")
    try:
        cur = conn.cursor()
        dbname = os.getenv('DB_NAME')
        if dbname is None:
            print("DB_NAME environment variable is not set")
            return
        # Convert the user_metadata set to a list and then to a JSON string
        alert_metadata_json = json.dumps(list(data))
        cur.execute(sql.SQL("""
            INSERT INTO {} (AlertMetadata) WHERE alertID = %d
            VALUES (%s)
        """).format(sql.Identifier(dbname)), (alertID, alert_metadata_json))
    except Exception as e:
        print("Error executing SQL query: ", e)
        return
    try:
        conn.commit()
    except Exception as e:
        print("Error committing transaction: ", e)
        return
    print("Completed, alert data added to the table.")

def output_alertdata_to_db(alertID, data):
    db_credentials = {
        'host': os.getenv('DB_HOST'),
        'port': os.getenv('DB_PORT'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASS'),
        'dbname': os.getenv('DB_NAME'),
    }
    print("Attempting to connect to the database...")
    conn = psycopg2.connect(**db_credentials)
    if conn:
        print("Connected to the new database. Attempting to write alert data...")
        db_alertdata_write(conn, alertID, data)
        print("Alert data written. Closing connection...")
        conn.close()

vertexai.init(project="ba-glass-hack24por-2011", location="us-central1")
parameters = {
    "max_output_tokens": 256,
    "temperature": 0.2,
    "top_p": 0.95,
    "top_k": 40
}
model = TextGenerationModel.from_pretrained("text-bison@001")
report = input("Insert Prompt")
response = model.predict(
    f""""We have a report from people of the glass factory floor and we need to extract data in json format in the following order: time(24 format), type_of_incident, location, if appliable the solution of that problem, and the shift. The shift normally is a letter A,B,C,D. The location two letters that represent the factory, number of the oven, the line, the section and the concavity, that is a letter A B or C. The keys must be in english but the data remains in the original language of input. The solution type and the problem type must be a short description in the language of input. The data should be in present tense.

Provide a summary with about two sentences for the following article: Ocorreu um erro nas mangueiras de assentamento do AV538C e paramos a producao para corrigir
Summary: ```json
[
  {
    "\"Time\": \"Não disponível\","
    "\"type_of_incident\": \"erro mangueiras de assentamento\","
    "\"location\": \"AV538C\","
    "\"solution\": \"Interrupção da Produção para manutenção\","
    "\"shift\": \"ãNo disponível\""
  }
]
```


Provide a summary with about two sentences for the following article: o defletor da estacao av893 empancou e tivemos que parar a producao para lubrificar o defleto. ocorreu no turno C
Summary: ```json
[
  {
    "\"Time\": \"Não disponível\","
    "\"type_of_incident\": \"Encravamento do defletor da estação\","
    "\"location\": \"AV893\","
    "\"solution\": \"Interupção da produção para lubrificação do defletor\","
    "\"shift\": \"C\""
  }
]
```


Provide a summary with about two sentences for the following article: no av52 no setor 8 por falha do rebentar da bola na cavidade A e braco de marizas partido.
Summary: ```json
[
  {
    "\"Time\": \"Não disponível\","
    "\"type_of_incident\": \"Bola rebentada,  braço de marisa partido\","
    "\"location\": \"AV528A\","
    "\"solution\": \"Não disponível\","
    "\"shift\": \"Não disponível\""
  }
]
```


Provide a summary with about two sentences for the following article:  no setor av548 BTC com problemas de excesso de temperatura, fizemos a limpeza do circuito de água de arrefecimento para resolver. ocorreu no turno A
Summary: ```json
[
  {
    "\"Time\": \"Não disponível\","
    "\"type_of_incident\": \"Excesso de temperatura no BTC\","
    "\"location\": \"AV548\","
    "\"solution\": \"Limpeza do circuito de água de arrefecimento\","
    "\"shift\": \"A\""
  }
]
```


Provide a summary with about two sentences for the following article: no turno A na AV566A a gota estava torta entao procedemos ao centramento da gota.
Summary: ```json
[
  {
    "\"Time\": \"Não disponível\","
    "\"type_of_incident\": \"Gota Desalinhada\","
    "\"location\": \"AV566A\","
    "\"solution\": \"Centragem da gota\","
    "\"shift\": \"A\""
  }
]
```


Provide a summary with about two sentences for the following article: no av456A, puncao demasiado quente, paramos o setor para aumentar 5º no 
 arrefecimento de ventilação na punção 
Summary: ```json
[
  {
    "\"Time\": \"Não disponível\","
    "\"type_of_incident\": \"Punção demasiado quente\","
    "\"location\": \"AV456A\","
    "\"solution\": \"Aumentar 5ºC no arrefecimento de ventilação na punção\","
    "\"shift\": \"Não disponível\""
  }
]
```

Provide a summary with about two sentences for the following article: {report}
Summary:
""",
    **parameters
)
print(f"Response from Model: {response.text}")
# send reponse to db
alertID = 1
output_alertdata_to_db(alertID, response.text)

