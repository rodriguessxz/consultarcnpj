from flask import Flask, request, jsonify, render_template
import requests

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/consultar', methods=['POST'])
def consultar_cnpjs():
    dados = request.get_json()
    cnpjs = dados.get('cnpjs', [])

    resultados = []

    for cnpj in cnpjs:
        try:
            url = f"https://www.receitaws.com.br/v1/cnpj/{cnpj}"
            response = requests.get(url, timeout=10)

            if response.status_code != 200:
                resultados.append({
                    "cnpj": cnpj,
                    "nome": "Erro na consulta",
                    "status": "Erro",
                    "telefone": "-",
                    "endereco": "-",
                    "atividade": "-"
                })
                continue

            info = response.json()

            if 'status' in info and info['status'] == 'ERROR':
                resultados.append({
                    "cnpj": cnpj,
                    "nome": info.get('message', 'Erro'),
                    "status": "Inválido",
                    "telefone": "-",
                    "endereco": "-",
                    "atividade": "-"
                })
                continue

            endereco = f"{info.get('logradouro', '')}, {info.get('numero', '')}, {info.get('bairro', '')}, {info.get('municipio', '')} - {info.get('uf', '')}, {info.get('cep', '')}"
            
            atividade_principal = info.get('atividade_principal', [{}])[0]
            codigo_atividade = atividade_principal.get('code', '-')
            descricao_atividade = atividade_principal.get('text', '-')
            atividade = f"{codigo_atividade} - {descricao_atividade}"

            resultados.append({
                "cnpj": cnpj,
                "nome": info.get('nome', '-'),
                "status": info.get('situacao', '-'),
                "telefone": info.get('telefone', '-'),
                "endereco": endereco,
                "atividade": atividade
            })

        except Exception as e:
            resultados.append({
                "cnpj": cnpj,
                "nome": "Erro na API",
                "status": "Erro",
                "telefone": "-",
                "endereco": "-",
                "atividade": "-"
            })

    return jsonify(resultados)

if __name__ == '__main__':
    app.run(debug=True)
