import bitstring as bs
import tree as tr
import time
import sys

#Gera o código de huffman (symbols é um dicionário com os símbolos e suas probabilidades)
def encoder(symbols):

  code = {key: bs.Bits(bin='0b') for key in symbols.keys()}

  list_symbols = [[x] for x in symbols.keys()]

  #Ordenando uma lista com conjuntos de simbolos de menor a maior valores de probalilidades somados do conjunto
  list_symbols = sorted(list_symbols, key= lambda k: sum(map(lambda x: symbols[x], k)))

  #0 para o símbolo de menor probabilidade
  for s in list_symbols[0]:
    code[s] += bs.Bits(bin='0b0')

  #1 para o segundo símbolo de menor probabilidade
  for s in list_symbols[1]:
    code[s] += bs.Bits(bin='0b1')

  #Supõe que existem mais de 2 símbolos inicialmente
  while len(list_symbols) > 2:

    new = list_symbols[0] + list_symbols[1] #Cria novo símbolo como a junção dos dois com menor probabilidade
    list_symbols = list_symbols[2:] #Tira os dois primeiros símbolos
    list_symbols.append(new) #Coloca novo símbolo
    list_symbols = sorted(list_symbols, key= lambda k: sum(map(lambda x: symbols[x], k))) #Ordena pela probabilidade com o novo símbolo combinado

    for s in list_symbols[0]:
      code[s] = bs.Bits(bin='0b0') + code[s]

    for s in list_symbols[1]:
      code[s] = bs.Bits(bin='0b1') + code[s]

  lengths = [value.len for key, value in sorted(code.items(),key= lambda x: x[0])] #Tamanhos dos códigos na ordem dos símbolos

  code, tree = tr.make_tree_code(code.keys(), lengths) #Gerando o código a ser utilizado

  symbols_being = bs.Bits(length= 256) #256bits para indicar quais dos 256 simbolos existem (1 se existe e 0 se não)
  for s in code:
    mask = bs.Bits(uint= 1, length= 256) << int.from_bytes(s, byteorder='big')
    symbols_being = symbols_being | mask
  
  lengths = b''.join(list(map(lambda x: x.to_bytes(1, byteorder= 'big'), lengths))) #Tamanhos dos códigos em bytes para ser escrito no arquivo

  return code, symbols_being, lengths #Dicionário com os símbolos e seus códigos + 256 bits indicando os símbolos existentes + bytestring com os tamanhos dos códigos desses símbolos

#---------------------------------------

#Gera a árvore e os códigos de Huffman a partir dos símbolos existentes e seus comprimentos
def gen_code_tree (list_symbols, lengths):

  return tr.make_tree_code (list_symbols, lengths) #Recria os códigos através dos tamanhos através de uma árvore

def decoder_two (file_bin, index, code, tree, end):

  values = []
  counter = 0

  #Dicionario com o codigo como chave e o símbolo como valor
  inv_dict_code = {_code: symbol for symbol, _code in code.items()}

  node = tree #Colocando o nó na raiz

  #Percorre os bits a partir de index e sai se já foram achados dois valores
  while index < end and counter < 2:

    #Percorre árvore se 0 para a esquerda e se 1 para a direita.
    if file_bin[index]:
        node = node.r_node
    else: node = node.l_node

    index += 1

    #Quando o nó não tem filho, pega o código do nó, escreve o símbolo correspondente no arquivo e volta para a raiz.
    if not node.have_children:
      values.append(inv_dict_code[node.value])
      node = tree
      counter += 1

  return values, index #Retorna os dois valores decodificados e o indice do proximo bit