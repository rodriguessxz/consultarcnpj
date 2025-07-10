from flask import Flask, request, jsonify, render_template
import requests
import time

app = Flask(__name__)

API_URL = "https://www.receitaws.com.br/v1/cnpj/{}"

def consultar_cnpj(cnpj):
    cnpj_limpo = ''.join(filter(str.isdigit, cnpj))
    if len(cnpj_limpo) != 14:
        return {
            "cnpj": cnpj,
            "nome": None,
            "status": None,
            "telefone": None,
            "atividade_principal": None,
            "erro": "CNPJ inválido"
        }
    try:
        r = requests.get(API_URL.format(cnpj_limpo))
        if r.status_code == 200:
            data = r.json()
            if data.get("status") == "OK":
                return {
                    "cnpj": cnpj_limpo,
                    "nome": data.get("nome"),
                    "status": data.get("situacao"),
                    "telefone": data.get("telefone"),
                    "atividade_principal": {
                        "codigo": data.get("atividade_principal", [{}])[0].get("code"),
                        "descricao": data.get("atividade_principal", [{}])[0].get("text")
                    },
                    "erro": None
                }
            else:
                return {
                    "cnpj": cnpj_limpo,
                    "nome": None,
                    "status": None,
                    "telefone": None,
                    "atividade_principal": None,
                    "erro": data.get("message", "Erro na consulta")
                }
        else:
            return {
                "cnpj": cnpj_limpo,
                "nome": None,
                "status": None,
                "telefone": None,
                "atividade_principal": None,
                "erro": f"Erro na requisição HTTP: {r.status_code}"
            }
    except Exception as e:
        return {
            "cnpj": cnpj_limpo,
            "nome": None,
            "status": None,
            "telefone": None,
            "atividade_principal": None,
            "erro": str(e)
        }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/consultar', methods=['POST'])
def consultar():
    data = request.get_json()
    if not data:
        return jsonify({"erro": "Requisição sem JSON válido"}), 400

    cnpjs_raw = data.get('cnpjs')
    if not cnpjs_raw:
        return jsonify({"erro": "Nenhum CNPJ enviado"}), 400

    if isinstance(cnpjs_raw, str):
        cnpjs_list = [c.strip() for c in cnpjs_raw.replace(',', '\n').split('\n') if c.strip()]
    elif isinstance(cnpjs_raw, list):
        cnpjs_list = [c.strip() for c in cnpjs_raw if isinstance(c, str) and c.strip()]
    else:
        return jsonify({"erro": "Formato do campo 'cnpjs' inválido"}), 400

    resultados = []
    for i, cnpj in enumerate(cnpjs_list):
        res = consultar_cnpj(cnpj)
        resultados.append(res)
        if i < len(cnpjs_list) - 1:
            time.sleep(20)

    return jsonify(resultados)

if __name__ == '__main__':
    app.run(debug=True)
