from transformers import AutoTokenizer  # Importa a classe AutoTokenizer da biblioteca transformers, usada para tokenizar texto.
import gradio as gr  # Importa a biblioteca gradio para criar interfaces web interativas e a associa ao alias 'gr'.

class ArithmeticInterpreter:  # Define uma classe chamada ArithmeticInterpreter para encapsular a lógica do interpretador.
    def __init__(self, model_name="bert-base-uncased"):  # Define o método construtor da classe, inicializando o objeto.
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)  # Carrega um tokenizer pré-treinado do Hugging Face com o nome do modelo especificado.
        self.operators = {'+': lambda a, b: a + b,  # Define um dicionário de operadores, mapeando símbolos a funções lambda.
                          '-': lambda a, b: a - b,
                          '*': lambda a, b: a * b,
                          '/': lambda a, b: a / b}

    def tokenize(self, expression):  # Define um método para tokenizar uma expressão aritmética.
        spaced_expression = ""  # Inicializa uma string vazia para armazenar a expressão com espaços.
        for char in expression:  # Itera sobre cada caractere na expressão de entrada.
            if char in self.operators or char in "()":  # Verifica se o caractere é um operador ou um parêntese.
                spaced_expression += f" {char} "  # Adiciona o caractere com espaços ao redor na string.
            else:
                spaced_expression += char  # Adiciona o caractere diretamente na string.
        return self.tokenizer.tokenize(spaced_expression)  # Usa o tokenizer carregado para dividir a string em tokens e retorna a lista de tokens.

    def evaluate(self, tokens):  # Define um método para avaliar uma lista de tokens representando uma expressão aritmética.
        def precedence(operator):  # Define uma função interna para determinar a precedência dos operadores.
            if operator in ('+', '-'):  # Adição e subtração têm precedência 1.
                return 1
            elif operator in ('*', '/'):  # Multiplicação e divisão têm precedência 2.
                return 2
            return 0  # Outros tokens têm precedência 0.

        def apply_op(operators, values):  # Define uma função interna para aplicar um operador aos dois últimos valores.
            operator = operators.pop()  # Obtém o último operador da pilha de operadores.
            right_operand = values.pop()  # Obtém o último valor (operando direito) da pilha de valores.
            left_operand = values.pop()  # Obtém o penúltimo valor (operando esquerdo) da pilha de valores.
            values.append(self.operators[operator](left_operand, right_operand))  # Aplica a operação e empurra o resultado de volta na pilha de valores.

        values = []  # Inicializa uma lista vazia para atuar como pilha de valores (operandos).
        operators = []  # Inicializa uma lista vazia para atuar como pilha de operadores.
        i = 0  # Inicializa um índice para percorrer os tokens.
        while i < len(tokens):  # Loop através de cada token na lista de tokens.
            token = tokens[i]  # Obtém o token atual.
            if token.isdigit() or (token.startswith('-') and token[1:].isdigit()):  # Verifica se o token é um número (positivo ou negativo).
                values.append(float(token))  # Converte o token para float e o adiciona à pilha de valores.
            elif token == '(':  # Se o token for um parêntese de abertura.
                operators.append(token)  # Adiciona o parêntese à pilha de operadores.
            elif token == ')':  # Se o token for um parêntese de fechamento.
                while operators and operators[-1] != '(':  # Enquanto houver operadores na pilha e o último não for um parêntese de abertura.
                    apply_op(operators, values)  # Aplica o último operador.
                operators.pop()  # Remove o parêntese de abertura da pilha de operadores.
            elif token in self.operators:  # Se o token for um operador.
                while operators and precedence(operators[-1]) >= precedence(token):  # Enquanto houver operadores com precedência maior ou igual na pilha.
                    apply_op(operators, values)  # Aplica esses operadores primeiro.
                operators.append(token)  # Adiciona o operador atual à pilha de operadores.
            i += 1  # Incrementa o índice para o próximo token.

        while operators:  # Enquanto ainda houver operadores na pilha após processar todos os tokens.
            apply_op(operators, values)  # Aplica os operadores restantes.

        return values[0]  # Retorna o único valor restante na pilha de valores, que é o resultado da expressão.

    def interpret(self, expression):  # Define um método para interpretar uma expressão aritmética completa.
        tokens = self.tokenize(expression)  # Tokeniza a expressão usando o método tokenize.
        try:
            result = self.evaluate(tokens)  # Avalia a lista de tokens usando o método evaluate.
            return result, tokens  # Retorna o resultado da avaliação e a lista de tokens.
        except (IndexError, TypeError):  # Captura erros de índice ou tipo que podem ocorrer em expressões mal formadas.
            return "Erro: Expressão mal formada.", tokens  # Retorna uma mensagem de erro e a lista de tokens.

# Cria uma instância da classe ArithmeticInterpreter.
interpreter = ArithmeticInterpreter()

# Define uma função que será usada pela interface Gradio para processar a entrada do usuário.
def process_expression(expression):
    result, tokens = interpreter.interpret(expression)  # Chama o método interpret para obter o resultado e os tokens.
    return result, tokens  # Retorna o resultado e os tokens para serem exibidos na interface Gradio.

# Define a interface Gradio.
iface = gr.Interface(
    fn=process_expression,  # Especifica a função a ser chamada quando a entrada é fornecida.
    inputs=gr.Textbox(label="Digite a expressão aritmética:"),  # Define um campo de texto como entrada com um rótulo.
    outputs=[  # Define uma lista de componentes de saída.
        gr.Textbox(label="Resultado:"),  # Um campo de texto para exibir o resultado da avaliação.
        gr.Textbox(label="Tokens:")  # Um campo de texto para exibir a lista de tokens gerados.
    ]
)

# Inicia a interface Gradio.
iface.launch(share=True)  # Lança a interface web no navegador, com a opção de criar um link público compartilhável.
