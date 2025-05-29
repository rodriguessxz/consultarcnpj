from flask import Flask, request, jsonify, render_template
import requests
import time

app = Flask(__name__)

API_URL = "https://www.receitaws.com.br/v1/cnpj/{}"

def consultar_cnpj(cnpj):
    cnpj_limpo = ''.join(filter(str.isdigit, cnpj))
    if len(cnpj_limpo) != 14:
        return {"cnpj": cnpj, "erro": "CNPJ inválido"}
    try:
        r = requests.get(API_URL.format(cnpj_limpo))
        if r.status_code == 200:
            data = r.json()
            if data.get("status") == "OK":
                return {
                    "cnpj": cnpj_limpo,
                    "nome": data.get("nome"),
                    "situacao": data.get("situacao"),
                    "telefone": data.get("telefone"),
                    "erro": None
                }
            else:
                return {"cnpj": cnpj_limpo, "erro": data.get("message", "Erro na consulta")}
        else:
            return {"cnpj": cnpj_limpo, "erro": "Erro na requisição"}
    except Exception as e:
        return {"cnpj": cnpj_limpo, "erro": str(e)}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/consultar', methods=['POST'])
def consultar():
    cnpjs = request.json.get('cnpjs', '')
    lista_cnpjs = [c.strip() for c in cnpjs.replace(',', '\n').split('\n') if c.strip()]
    resultados = []
    for idx, cnpj in enumerate(lista_cnpjs):
        res = consultar_cnpj(cnpj)
        resultados.append(res)
        # Delay reduzido para 20s entre 3 consultas = 6-7 segundos por consulta
        if idx < len(lista_cnpjs) - 1:
            time.sleep(7)
    return jsonify(resultados)

if __name__ == '__main__':
    app.run(debug=True)
