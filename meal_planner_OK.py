import tkinter as tk
from tkinter import ttk, messagebox
import csv

# Fonction pour charger les repas depuis le fichier CSV
def load_meals(file_path):
    meals = {}
    try:
        with open(file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                plat = row['Plat']
                ingredient = row['Ingrédient']
                quantite = row['Quantité']
                unite = row['Unité']
                if plat not in meals:
                    meals[plat] = []
                meals[plat].append((ingredient, quantite, unite))
        print("Repas chargés depuis le fichier CSV:")
        for plat, ingredients in meals.items():
            print(f"{plat}:")
            for ingredient, quantite, unite in ingredients:
                print(f"  - {ingredient}: {quantite} {unite}")
    except Exception as e:
        print(f"Erreur lors du chargement des repas: {e}")
        messagebox.showerror("Erreur", f"Erreur lors du chargement des repas: {e}")
    return meals

# Fonction pour générer la liste de courses
def generate_shopping_list(selected_meals, all_meals):
    shopping_list = {}
    for meal in selected_meals:
        if meal in all_meals:
            ingredients = all_meals[meal]
            for ingredient, quantite, unite in ingredients:
                if ingredient in shopping_list:
                    shopping_list[ingredient][0] += float(quantite)
                else:
                    shopping_list[ingredient] = [float(quantite), unite]
    print(f"Liste de courses générée : {shopping_list}")  # Débogage
    return shopping_list

# Fonction pour exporter la liste de courses en fichier CSV
def export_shopping_list(shopping_list, file_path):
    try:
        with open(file_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Ingrédient', 'Quantité', 'Unité'])
            for ingredient, (quantite, unite) in shopping_list.items():
                writer.writerow([ingredient, quantite, unite])
        print("Liste de courses exportée avec succès!")  # Débogage
        messagebox.showinfo("Succès", "Liste de courses exportée avec succès!")
    except Exception as e:
        print(f"Erreur lors de l'exportation de la liste de courses: {e}")
        messagebox.showerror("Erreur", f"Erreur lors de l'exportation de la liste de courses: {e}")

# Fonction pour mettre à jour la liste de courses affichée
def update_shopping_list_display(tree, shopping_list):
    for item in tree.get_children():
        tree.delete(item)
    for ingredient, (quantite, unite) in shopping_list.items():
        tree.insert("", "end", values=(ingredient, quantite, unite))

# Fonction pour gérer le clic sur le bouton "Générer la liste de courses"
def on_generate_button_click(tree, meal_vars, all_meals):
    selected_meals = [meal for meal, var in meal_vars.items() if var.get()]
    print(f"Repas sélectionnés : {selected_meals}")  # Débogage
    shopping_list = generate_shopping_list(selected_meals, all_meals)
    update_shopping_list_display(tree, shopping_list)
    global current_shopping_list
    current_shopping_list = shopping_list

# Fonction pour gérer le clic sur le bouton "Exporter la liste de courses"
def on_export_button_click():
    if not current_shopping_list:
        messagebox.showwarning("Avertissement", "La liste de courses est vide. Sélectionnez des repas d'abord.")
        return
    
    # Exportation dans un fichier CSV
    try:
        with open('shopping_list.csv', mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Ingrédient', 'Quantité', 'Unité'])
            for ingredient, (quantite, unite) in current_shopping_list.items():
                writer.writerow([ingredient, quantite, unite])
        messagebox.showinfo("Export", "La liste de courses a été exportée avec succès sous le nom 'shopping_list.csv'.")
    except Exception as e:
        messagebox.showerror("Erreur", f"Une erreur est survenue lors de l'exportation : {e}")

# Initialisation de l'application Tkinter
root = tk.Tk()
root.title("Planificateur de repas")
root.geometry("800x600")

# Chargement des repas depuis le fichier CSV
meals_file = 'meals.csv'
all_meals = load_meals(meals_file)
print("Tous les repas sont chargés.")  # Débogage

# Variable globale pour stocker la liste de courses actuelle
current_shopping_list = {}

# Cadre pour la liste des repas avec une barre de défilement
frame_meals = ttk.LabelFrame(root, text="Sélectionnez les repas")
frame_meals.pack(fill="both", expand="yes", padx=10, pady=10)

canvas_meals = tk.Canvas(frame_meals)
scrollbar_meals = ttk.Scrollbar(frame_meals, orient="vertical", command=canvas_meals.yview)
scrollable_frame_meals = ttk.Frame(canvas_meals)

scrollable_frame_meals.bind(
    "<Configure>",
    lambda e: canvas_meals.configure(
        scrollregion=canvas_meals.bbox("all")
    )
)

canvas_meals.create_window((0, 0), window=scrollable_frame_meals, anchor="nw")
canvas_meals.configure(yscrollcommand=scrollbar_meals.set)

canvas_meals.pack(side="left", fill="both", expand=True)
scrollbar_meals.pack(side="right", fill="y")

# Liste des repas disponibles
meal_vars = {}
for meal in all_meals.keys():
    var = tk.BooleanVar()
    cb = ttk.Checkbutton(scrollable_frame_meals, text=meal, variable=var)
    cb.pack(anchor='w')
    meal_vars[meal] = var

# Cadre pour la liste de courses avec une barre de défilement
frame_shopping_list = ttk.LabelFrame(root, text="Liste de courses")
frame_shopping_list.pack(fill="both", expand="yes", padx=10, pady=10)

canvas_shopping_list = tk.Canvas(frame_shopping_list)
scrollbar_shopping_list = ttk.Scrollbar(frame_shopping_list, orient="vertical", command=canvas_shopping_list.yview)
scrollable_frame_shopping_list = ttk.Frame(canvas_shopping_list)

scrollable_frame_shopping_list.bind(
    "<Configure>",
    lambda e: canvas_shopping_list.configure(
        scrollregion=canvas_shopping_list.bbox("all")
    )
)

canvas_shopping_list.create_window((0, 0), window=scrollable_frame_shopping_list, anchor="nw")
canvas_shopping_list.configure(yscrollcommand=scrollbar_shopping_list.set)

canvas_shopping_list.pack(side="left", fill="both", expand=True)
scrollbar_shopping_list.pack(side="right", fill="y")

# Arbre pour afficher la liste de courses
tree = ttk.Treeview(scrollable_frame_shopping_list, columns=('Ingrédient', 'Quantité', 'Unité'), show='headings')
tree.heading('Ingrédient', text='Ingrédient')
tree.heading('Quantité', text='Quantité')
tree.heading('Unité', text='Unité')
tree.pack(fill="both", expand=True)

# Boutons pour générer et exporter la liste de courses
frame_buttons = ttk.Frame(root)
frame_buttons.pack(fill="x", padx=10, pady=10)

# Ajout du bouton pour générer la liste de courses
btn_generate = ttk.Button(frame_buttons, text="Générer la liste de courses", 
                          command=lambda: on_generate_button_click(tree, meal_vars, all_meals))
btn_generate.pack(side="left", padx=5)

# Ajout du bouton pour exporter la liste de courses
btn_export = ttk.Button(frame_buttons, text="Exporter la liste de courses", 
                        command=on_export_button_click)
btn_export.pack(side="right", padx=5)

root.mainloop()
