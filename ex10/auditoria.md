1. A05 - SQL Injection — a entrada do usuário era concatenada diretamente na consulta SQL. Correção: utilização de query parametrizada.

2. A05 - XSS — o valor recebido pelo parâmetro u era colocado diretamente no HTML. Correção: escape do conteúdo antes de renderizar.

3. A01 - Broken Access Control — a rota DELETE não exigia autenticação ou autorização. Correção: validação da API Key e do nível de acesso.

4. A10 - Mishandling of Exceptional Conditions — a aplicação podia devolver detalhes internos e traceback. Correção: tratamento das exceções e retorno de mensagem genérica.

5. A04 - Cryptographic Failures — a consulta retornava a coluna senha junto com os dados do usuário. Correção: selecionar somente as colunas necessárias.

6. A02 - Security Misconfiguration — a aplicação estava executando com debug=True e host 0.0.0.0. Correção: desabilitar o debug e limitar o host.

7. A09 - Security Logging and Alerting Failures — não havia registro adequado das ações sensíveis realizadas pela API. Correção: adicionar registros de auditoria para ações relevantes.

8. A02 - Credenciais hardcoded — SENHA_MESTRA e a senha do banco estavam escritas diretamente no código. Correção: mover credenciais para variáveis de ambiente.

9. A02 - Ausência de headers de segurança — a aplicação não enviava políticas de segurança HTTP. Correção: adicionar Content-Security-Policy, X-Content-Type-Options e X-Frame-Options.

10. A06 - Ausência de validação de entrada — as entradas recebidas pelas rotas não eram devidamente validadas antes de serem processadas. Correção: validar parâmetros e restringir os valores aceitos.
