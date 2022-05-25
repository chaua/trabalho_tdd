from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

from selenium.webdriver.support.select import Select

MAX_WAIT = 10


class NewVisitorTest(LiveServerTestCase):

    def setUp(self):
        self.browser = webdriver.Firefox()

    def tearDown(self):
        self.browser.quit()

    # Auxiliary method
    def wait_for_row_in_list_table(self, row_text):
        start_time = time.time()
        while True:
            try:
                table = self.browser.find_element_by_id('id_list_table')
                rows = table.find_elements_by_tag_name('tr')
                self.assertIn(row_text, [row.text for row in rows])
                return
            except(AssertionError, WebDriverException) as e:
                if time.time() - start_time > MAX_WAIT:
                    raise e
                time.sleep(0.5)

    def test_nova_situacao_problema(self):
        # Edith ouviu falar que agora a aplicação online de lista de tarefas
        # aceita definir prioridades nas tarefas do tipo baixa, média e alta
        # Ela decide verificar a homepage
        self.browser.get(self.live_server_url)

        # Ela percebe que o título da página e o cabeçalho mencionam
        # listas de tarefas com prioridade (priority to-do)
        self.assertIn('priority to-do', self.browser.title)
        header_text = self.browser.find_element(by=By.TAG_NAME, value='h1').text
        self.assertIn('priority to-do', header_text)

        # Ela é convidada a inserir um item de tarefa e a prioridade da
        # mesma imediatamente
        inputbox = self.browser.find_element(by=By.ID, value='id_new_item')
        self.assertEqual(inputbox.get_attribute('placeholder'), 'Enter a to-do item')

        selectbox = Select(self.browser.find_element(by=By.ID, value='prioridade'))

        # Ela digita "Comprar anzol" em uma nova caixa de texto
        # e assinala prioridade alta no campo de seleção de prioridades
        inputbox.send_keys('Comprar anzol')
        selectbox.select_by_visible_text('alta')

        # Quando ela tecla enter, a página é atualizada, e agora
        # a página lista "1 - Comprar anzol - prioridade alta"
        # como um item em uma lista de tarefas
        inputbox.send_keys(Keys.ENTER)
        self.wait_for_row_in_list_table('1 - Comprar anzol - prioridade alta')

        # Ainda continua havendo uma caixa de texto convidando-a a
        # acrescentar outro item. Ela insere "Comprar cola instantâne"
        # e assinala prioridade baixa pois ela ainda tem cola suficiente
        # por algum tempo
        inputbox = self.browser.find_element(by=By.ID, value='id_new_item')
        selectbox = Select(self.browser.find_element(by=By.ID, value='prioridade'))

        inputbox.send_keys("Comprar cola instantânea")
        selectbox.select_by_visible_text('baixa')

        inputbox.send_keys(Keys.ENTER)

        # A página é atualizada novamente e agora mostra os dois
        # itens em sua lista e as respectivas prioridades

        self.wait_for_row_in_list_table('1 - Comprar anzol - prioridade alta')
        self.wait_for_row_in_list_table('2 - Comprar cola instantânea - prioridade baixa')

    # Edith se pergunta se o site lembrará de sua lista. Então
    # ela nota que o site gerou um URL único para ela -- há um
    # pequeno texto explicativo para isso.

    # Ela acessa essa URL -- sua lista de tarefas continua lá.
    def test_multiple_users_can_start_lists_at_different_urls(self):
        # Edith inicia uma nova lista de tarefas
        self.browser.get(self.live_server_url)

        inputbox = self.browser.find_element(by=By.ID, value='id_new_item')
        selectbox = Select(self.browser.find_element(by=By.ID, value='prioridade'))
        inputbox.send_keys('Comprar anzol')
        selectbox.select_by_visible_text('alta')

        inputbox.send_keys(Keys.ENTER)
        self.wait_for_row_in_list_table('1 - Comprar anzol - prioridade alta')

        # Ela percebe que sua lista te um URL único
        edith_list_url = self.browser.current_url
        self.assertRegex(edith_list_url, '/lists/.+')

        # Agora um novo usuário, Francis, chega ao site

        ## Usamos uma nova versão do nagegador para garantir que nenhuma
        ## informação de Edith está vindo de cookies, etc

        self.browser.quit()
        self.browser = webdriver.Firefox()

        # Francis acessa a página inicial. Não há sinal da lista de Edith
        self.browser.get(self.live_server_url)
        page_text = self.browser.find_element(by=By.TAG_NAME, value='body').text
        self.assertNotIn('Comprar anzol', page_text)
        self.assertNotIn('prioridade alta', page_text)

        # Francis inicia uma nova lista inserindo um novo item.
        inputbox = self.browser.find_element(by=By.ID, value='id_new_item')
        selectbox = Select(self.browser.find_element(by=By.ID, value='prioridade'))
        inputbox.send_keys('Comprar leite')
        selectbox.select_by_visible_text('baixa')

        inputbox.send_keys(Keys.ENTER)
        self.wait_for_row_in_list_table('1 - Comprar leite - prioridade baixa')

        # Francis obtém seu próprio URL exclusivo
        francis_list_url = self.browser.current_url
        self.assertRegex(edith_list_url, '/lists/.+')
        self.assertNotEqual(francis_list_url, edith_list_url)

        # Novamente não há sinal algum da lista de Edith
        page_text = self.browser.find_element(by=By.TAG_NAME, value='body').text
        self.assertNotIn('Comprar anzol', page_text)
        self.assertIn('Comprar leite', page_text)

    # Fim
