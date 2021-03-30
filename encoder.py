import sys
import re

def main():
  
  filename = input("Informe o nome (caminho) do arquivo a ser comprimido: ")
  directory = input("Informe o nome do diretório do resultado (será o atual caso não informado): ")

  no_path_name = remove_path(filename)
  filename_result = add_path_bin(directory, no_path_name)

  try:
    with open(filename) as f_read:
      with open(filename_result, 'w') as f_write:
        pass

  except IOError as ioe:
    sys.exit('Arquivo ou diretório "{}" não existente.'.format(ioe.filename))


#--------------------------------------

def remove_path(filename):
  return re.split(r'\\|/', filename)[-1]

def add_path_bin(directory, no_path_name):
  bin_name = no_path_name + '.bin'
  return directory + '/' + bin_name if directory else bin_name

if __name__ == "__main__":
  main()