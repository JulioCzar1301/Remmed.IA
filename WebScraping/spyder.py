from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time
import re
import math
import os
import threading
from queue import Queue

# Caminho do driver local
CHROME_DRIVER_PATH = './chrome_driver/chromedriver.exe'

if __name__ == "__main__":
    base_path = "https://consultaremedios.com.br/medicamentos/"
    search_by_letter = ["a","b", "c",
        "d", "e", "f", "g", "h", "i", "j", "k", "l", "m",
        "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z","0-9"
    ]
    links_file = "links_medicamentos.txt"
    all_links = []

    chrome_options = Options()

    #Caso tenha um arquivo de links, ele lê ele ao invés de fazer o scraping novamente
    if os.path.exists(links_file):
        print("Lendo links do arquivo...")
        with open(links_file, 'r', encoding='utf-8') as f:
            for line in f:
                name, letter = line.strip().split('\t')
                all_links.append((name, letter))
    else:
        #Percorre todas as letras do alfabeto e números para pegar os links dos medicamentos
        for letter in search_by_letter:
            #Inicializa o driver do Chrome
            service = Service(CHROME_DRIVER_PATH)
            driver = webdriver.Chrome(service=service, options=chrome_options)
            #Pega a página inicial da letra
            driver.get(base_path + letter)
            time.sleep(0.5)
            #Obtem a lista de medicamentos
            ul = driver.find_element(By.XPATH, '//section/div[2]/div/div/ul')
            medicines = ul.find_elements(By.TAG_NAME, "li")
            #Obtem o número total de medicamentos e calcula o número de páginas
            pages = driver.find_element(By.XPATH, '//section/div[3]/div/div[2]/p/span[5]')
            number = int(re.search(r'\d+', pages.text).group())
            total_number = math.ceil((number)/40)
            #Percorre os medicamentos da primeira página
            for medicine in medicines:
                name = medicine.find_element(By.TAG_NAME, "a").get_attribute("href")
                print(f"Medicamento: {name}")
                #Adiciona o link e a letra à lista
                all_links.append((name, letter))

            #Se houver mais de uma página, percorre as páginas restantes
            if(total_number > 1):
                for page in range(2, total_number + 1):
                    driver.get(f"{base_path}{letter}?pagina={page}")
                    time.sleep(0.5)
                    try:
                        ul = driver.find_element(By.XPATH, '//section/div[2]/div/div/ul')
                        medicines = ul.find_elements(By.TAG_NAME, "li")
                        for medicine in medicines:
                            name = medicine.find_element(By.TAG_NAME, "a").get_attribute("href")
                            print(f"Medicamento: {name}")
                            all_links.append((name, letter))
                    except Exception as e:
                        print(f"Erro ao processar página {page}: {e}")
                    print("--------------------------------")
                    print(f"Página {page} de {total_number} processada.")
                    print("--------------------------------")
        driver.quit()
        # Salvar links em arquivo
        with open(links_file, 'w', encoding='utf-8') as f:
            for name, letter in all_links:
                f.write(f"{name}\t{letter}\n")


print(f"[INFO] Total de links coletados: {len(all_links)}")

# === 2. Visitar cada link e salvar bula ===
print("[INFO] Iniciando extração das bulas...")


# Multithreading para processar várias janelas Chrome
def worker(queue, lock, total):
    chrome_options = Options()
    driver = webdriver.Chrome(service=Service(CHROME_DRIVER_PATH), options=chrome_options)
    
    #Inicia o loop de processamento dos links
    while True:
        item = queue.get()
        
        #Verifica se o item é None, indicando que deve sair do loop
        if item is None:
            break

        #Atribui o índice e o link do medicamento
        idx, (name, letra) = item

        try:
            medicine_name = name.rstrip('/').split('/')[-2]
            destination_folder = os.path.join('medicamentos', letra)
            os.makedirs( destination_folder, exist_ok=True)
            file_path = os.path.join(destination_folder, f"{medicine_name }.txt")
            
            #Verifica se o arquivo já existe, se sim, pula para o próximo
            if os.path.exists(file_path):
                with lock:
                    print(f"[{idx}/{total}] Arquivo já existe, pulando: {file_path}")
                queue.task_done()
                continue

            url_bula = name.rstrip('/')
            
            #Obtem a URL correta da bula
            if url_bula.endswith('/p'):
                url_bula = url_bula[:-2] + '/bula'
            else:
                url_bula = url_bula + '/bula'

            with lock:
                print(f"[{idx}/{total}] Acessando: {url_bula}")
            
            #Pega a página da bula
            driver.get(url_bula)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "leaflet-article"))
            )
            #Minera o conteúdo relevante da bula
            div_pai = driver.find_element(By.CLASS_NAME, "leaflet-article")
            conteudo_textual = []
            classes_divs_filhas = [
                'para-que-serve', 'como-funciona', 'contraindicacao', 'posologia-como-usar'
            ]

            for class_filha in classes_divs_filhas:

                try:
                    div_filha = div_pai.find_element(By.ID, class_filha)
                    texto = div_filha.text.strip()

                    if texto:
                        conteudo_textual.append(texto)

                except Exception as e:
                    with lock:
                        print(f"Div filha com classe '{class_filha}' não encontrada ou sem texto: {e}")

            texto_final = "\n\n\n".join(conteudo_textual)

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(texto_final)

            with lock:
                print(f"[{idx}/{total}] Salvo em: {file_path}")

        except Exception as e:
            with lock:
                print(f"[ERRO] Falha ao processar {name}: {e}")

        queue.task_done()
    driver.quit()

#Define o número de threads e inicializa a fila e o lock
num_threads = 5
queue = Queue()
lock = threading.Lock()
total = len(all_links)
threads = []

#Loop para iniciar as threads
for _ in range(num_threads):
    t = threading.Thread(target=worker, args=(queue, lock, total))
    t.start()
    threads.append(t)

#Adiciona os links à fila
for idx, item in enumerate(all_links, start=1):
    queue.put((idx, item))
queue.join()

#Adiciona None à fila para cada thread, indicando que devem sair do loop
for _ in range(num_threads):
    queue.put(None)

#Aguarda todas as threads terminarem
for t in threads:
    t.join()

print("[INFO] Processo finalizado.")
