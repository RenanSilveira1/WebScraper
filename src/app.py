import tkinter as tk
from tkinter import messagebox, scrolledtext
import wikipedia
from dataclasses import dataclass
from typing import Optional

# ===== Domínio / Model =====
@dataclass
class SearchResult:
    title: str
    url: str
    summary: str
    additional_info: Optional[str] = None

# ===== Serviço / Interface =====
class WikipediaServiceInterface:
    def fetch_summary(self, term: str) -> SearchResult:
        raise NotImplementedError("Subclasses devem implementar este método")

# ===== Serviço / Implementação =====
class WikipediaService(WikipediaServiceInterface):
    def __init__(self, language: str = "pt"):
        # Configura a Wikipedia para o idioma desejado
        wikipedia.set_lang(language)
    
    def fetch_summary(self, term: str) -> SearchResult:
        try:
            page = wikipedia.page(term)
            return SearchResult(title=page.title, url=page.url, summary=page.summary)
        except wikipedia.exceptions.DisambiguationError as e:
            options = "\n".join(e.options)
            return SearchResult(
                title=term,
                url="",
                summary=f"O termo '{term}' é ambíguo. Tente especificar melhor. Opções sugeridas:\n{options}"
            )
        except wikipedia.exceptions.PageError:
            return SearchResult(
                title=term,
                url="",
                summary=f"Não foi encontrada uma página para o termo '{term}'."
            )

# ===== Interface Gráfica / Apresentação =====
class FastSearchUI:
    def __init__(self, service: WikipediaServiceInterface):
        # Injeção de dependência: a UI depende de uma abstração do serviço
        self.service = service
        self.root = tk.Tk()
        self._configure_ui()
    
    def _configure_ui(self):
        self.root.title("Fast Search")
        self.root.geometry("700x500")
        
        # Título da aplicação
        title_label = tk.Label(self.root, text="Fast Search", font=("Arial", 18, "bold"))
        title_label.pack(pady=10)
        
        # Frame para o campo de busca e botão "Search"
        search_frame = tk.Frame(self.root)
        search_frame.pack(pady=5)
        
        self.entry = tk.Entry(search_frame, width=50, font=("Arial", 12))
        self.entry.pack(side=tk.LEFT, padx=5)
        
        search_button = tk.Button(search_frame, text="Search", font=("Arial", 12), command=self._on_search)
        search_button.pack(side=tk.LEFT, padx=5)
        
        # Área de texto para exibir os resultados
        self.text_area = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, width=80, height=20, font=("Arial", 11))
        self.text_area.pack(pady=10, padx=10)
        
        # Botão para sair da aplicação
        exit_button = tk.Button(self.root, text="Sair", font=("Arial", 12), command=self.root.destroy)
        exit_button.pack(pady=5)
    
    def _on_search(self):
        term = self.entry.get().strip()
        if not term:
            messagebox.showwarning("Aviso", "Por favor, digite um termo para buscar.")
            return
        
        # Limpa a área de texto antes de exibir um novo resultado
        self.text_area.delete('1.0', tk.END)
        
        # Usa o serviço para buscar o resumo da Wikipedia
        result = self.service.fetch_summary(term)
        
        # Formata o texto a ser exibido
        display_text = f"Título: {result.title}\n"
        if result.url:
            display_text += f"URL: {result.url}\n"
        display_text += f"\nResumo:\n{result.summary}"
        
        self.text_area.insert(tk.END, display_text)
    
    def run(self):
        self.root.mainloop()

# ===== Ponto de Entrada =====
def main():
    # Injeção de dependência: instanciamos o serviço e passamos para a UI
    service = WikipediaService(language="pt")
    app = FastSearchUI(service)
    app.run()

if __name__ == "__main__":
    main()
