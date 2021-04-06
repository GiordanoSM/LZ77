import sys
import re
import time
import bitstring as bs
import my_huffman as mh #Codigo de huffman do trabalho 1 adaptado para a utilização no contexto do LZ77

def main():  
  filename = input("Informe o nome (caminho) do arquivo a ser descomprimido: ")
  directory = input("Informe o nome do diretório do resultado (será o atual caso não informado): ")

  no_path_name = remove_path(filename) #Adquire somente o nome do arquivo em a ser lido
  filename_result = add_path_rmv_bin(directory, no_path_name) #Extrai o nome do novo arquivo descomprimido junto com o diretório alvo

  if no_path_name[-4:] != '.bin': #Verifica se a extensão do arquivo a ser lido é a esperada
    sys.exit('Erro: Esperado arquivo de extensão: ".bin".')

  try:
    with open(filename_result, 'wb') as f_write:
      bits_header = bs.Bits(filename= filename, length= 8) #Lê o primeiro byte do arquivo
      
      padding = check_header(bits_header) #Retira as informações do header

      _list = bs.Bits(filename= filename, offset= 8,  length= 256) #Lê os 256 bits que indicam os símbolos (Huffman)
      list_symbols = get_symbols(_list) #Extrai quais são os símbolos (Huffman)

      bits_lengths = bs.Bits(filename= filename, offset= 264, length= len(list_symbols)*8) #Lê os tamanhos dos códigos (Huffman)
      lengths = get_lengths(bits_lengths) #Extrai os tamanhos dos códigos (Huffman)

      file_bin = bs.Bits(filename= filename, offset= 264 + len(list_symbols)*8) #Lê o resto do arquivo (Isso não traz para a memória o arquivo todo de uma vez)

      decode(file_bin, f_write, padding, list_symbols, lengths) #Decodifica o LZ77 e o Huffman utilizados, escrevendo o resultado no arquivo alvo

  except IOError as ioe:
    sys.exit('Erro: Arquivo ou diretório "{}" não existente.'.format(ioe.filename))

  except WrongHeader:
    sys.exit('Erro: Header do arquivo não condiz com o esperado.')

  print("Terminado! Criado arquivo '{}'.\n".format(filename_result))

#-----------------------------
#Retira parte do nome do arquivo que indica o caminho
def remove_path(filename):
  return re.split(r'\\|/', filename)[-1]

#Retira a extensão .bin e adiciona o diretório alvo no novo arquivo
def add_path_rmv_bin(directory, no_path_name):
  no_bin_name = no_path_name[:-4]
  return directory + '/' + no_bin_name if directory else no_bin_name

#Recebe os arquivos para leitura e escrita, o padding do arquivo de leitura, e a lista dos símbolos e comprimentos do código de Huffman 
def decode(file_bin, f_write, padding, list_symbols, lengths):
  print('Decodificando... (pode demorar)')
  start = time.time()

  #Seleciona o valor do comprimento máximo do Search Buffer utilizado na compressão
  if len(sys.argv) > 1:
    search_buffer_max = min(int(sys.argv[1]), 255)
  else:
    search_buffer_max = 16
  search_buffer = []

  #Gera o código de Huffman e a árvore utilizadas na compressão
  code, tree = mh.gen_code_tree(list_symbols, lengths)

  end = file_bin.len - padding #Id do final do arquivo
  
  count = 0 #Indice no arquivo de leitura

  #Dicionario com o codigo como chave e o símbolo como valor
  inv_dict_code = {_code: symbol for symbol, _code in code.items()}

  #Percorre o arquivo de leitura
  while count < end:
    #Realiza a decodificação do código de huffman de dois elementos, atualizando a posição no arquivo (count)
    values, count = mh.decoder_two(file_bin, count, inv_dict_code, tree, end)

    index = int.from_bytes(values[0],byteorder='big')
    size = int.from_bytes(values[1],byteorder='big')

    next_s = file_bin[count:count + 8].tobytes() #Lê o símbolo que vem após o casamento (não codificado) 
    count += 8 #Atualiza o contador

    #Se o índice informado for de um símbolo presente no Search Buffer (ou seja, diferente de 0)
    if index > 0:
      #Adapta o índice para a numeração dos índices da lista utilizada já que ela é montada a partir do seu final e não do início
      index = len(search_buffer) - index # (Ex: Faz com que o índice 1 seja a última posição na nossa lista)

      #Para cada elemento do casamento, adiciona ao final do Search Buffer e escreve no arquivo alvo
      for i in range(size):
        search_buffer.append(search_buffer[index + i])
        f_write.write(search_buffer[index + i])

    #Escreve o próximo símbolo no Search Buffer e no arquivo alvo
    search_buffer.append(next_s)
    f_write.write(next_s)

    #Caso o tamanho do Search Buffer seja maior do que o máximo informado, diminui para esse máximo a fim de não trazer todo o arquivo para a memória
    if len(search_buffer) >= search_buffer_max:
        search_buffer = search_buffer[len(search_buffer) - search_buffer_max:]
  
  end = time.time()
  print('Demorou: {} segundos'.format(end - start))

  #print(search_buffer)

#Checa se o header corresponde com o esperado e retorna o padding informado por ele
def check_header(header):

  if header[:-4] == bs.Bits(hex= '0xf'):
    return header[4:].uint

  else: raise WrongHeader

class WrongHeader(Exception):
  pass

#Extrai os símbolos presentes que foram codificados (Huffman)
def get_symbols(_list):

  int_little = list(_list.findall('0b1')) #inteiros dos símbolos lidos na byteordem 'litte'

  symbols = [(255-s).to_bytes(1, byteorder= 'big') for s in int_little] #símbolos presentes em bytes

  return symbols

#Retorna um array de inteiros com os tamanhos de códigos existentes (Huffman)
def get_lengths(bits_lengths):

  lengths = []

  for b in bits_lengths.tobytes():
    lengths.append(b)

  return lengths

if __name__ == "__main__":
  main()