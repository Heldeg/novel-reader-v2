import PySimpleGUI as sg
import scraping
import ebooks_creator
import novel_info

# TODO: check cap num

sg.theme('Dark2')

layout = [
    [sg.Text('URL'), sg.InputText(key="ch_url", size=(70, 1)), sg.Button("Obtener")],
    [sg.Text('Capítulo'), sg.Text('', key='num_chapter')],
    [sg.Text('Directorio'), sg.InputText(key='-NOVEL FOLDER-', size=(70, 1)),
     sg.FolderBrowse(initial_folder=novel_info.working_directory, key="folder", target='-NOVEL FOLDER-'),
     sg.Button('Traer información')],
    [sg.Text('Título novela'), sg.InputText(key='title', size=(70, 1))],
    [sg.Text('Nombre alternativo'), sg.InputText('', key='alternative_name', size=(70, 1))],
    [sg.Text('Autor'), sg.InputText('', key='author', size=(70, 1))],
    [sg.Text('Número de capítulos'), sg.InputText('100', key='num', size=(70, 1))],
    [sg.Button('Guardar Información'), sg.Button('Crear libro'), sg.Text('', key='status')]
]
window = sg.Window('Lector de Novelas', layout)
next_url = ''


def create_book(values):
    chapter_list = []
    num_caps = int(values['num'])
    chapter_url = values["ch_url"]
    for i in range(num_caps):
        text, title_num, next_ch_url = scraping.get_chapter(chapter_url)
        if i == 0:
            start_ch = int(scraping.curren_chapter)
            end_ch = (num_caps + start_ch) - 1
            book = ebooks_creator.setup_book(values['title'], values['author'], (start_ch, end_ch),
                                        values['-NOVEL FOLDER-'] + '/cover.jpg')
            book_name = f"{values['alternative_name']} {start_ch} - {end_ch}.epub"    
        chapter = ebooks_creator.create_new_chapter(title_num[0].title(), text, title_num[1])
        chapter_list.append(chapter)
        book.add_item(chapter)
        chapter_url = next_ch_url
        window['status'].update(f'{(i / num_caps) * 100:.1f}%')
        window.refresh()
    folder = values['-NOVEL FOLDER-']
    ebooks_creator.complete_book(chapter_list, folder, book_name, book)
    return chapter_url


def save():
    novel_info.save_info(values['title'], values['alternative_name'], next_url, values['author'])
    window['status'].update("Archivo guardado")


def get_book_info():
    global next_url, chapter_num
    content, title, next_url = scraping.get_chapter(values["ch_url"])
    window["num_chapter"].update(title[0])
    window['status'].update("Ok")

if __name__ == "__main__":
    while True:
        event, values = window.read()
        if event == 'Obtener':
            get_book_info()

        if event == 'Traer información':
            directory = values['-NOVEL FOLDER-']
            data = novel_info.read_novel_info(directory)

            window["title"].update(data['title'])
            window['author'].update(data['author'])
            window['ch_url'].update(data['last_url'])
            window['alternative_name'].update(data['alt_title'])
        if event == 'Guardar Información':
            save()
        if event == 'Crear libro':
            window.disable()
            next_url = create_book(values)
            window.enable()
            save()

        if event == sg.WIN_CLOSED:
            break
    window.close()
