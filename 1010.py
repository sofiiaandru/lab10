import telebot
import threading
import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import time


token = "7787807272:AAG6qXR47f8WpjjZt0OijdrBtTvYqVyeTXg"
bot = telebot.TeleBot(token)
user_role = {}
admin_password = "admin"

user_roles = {} 
def table_names():
    conn = sqlite3.connect(r"D:\ФІТ 1-11\Андрущенко\NPC.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [name[0] for name in cursor.fetchall()]
    conn.close()
    return tables
def select_data(table_name, columns, where=None ):
    conn = sqlite3.connect(r"D:\ФІТ 1-11\Андрущенко\NPC.db")
    cursor = conn.cursor()
    req = f"SELECT {columns} FROM {table_name}"
    if where:
        req += f" WHERE {where}"
    cursor.execute(req)
    results = cursor.fetchall()
    for row in results:
        print(row)
    conn.close()
    return results  
def get_column_names(table_name):
    conn = sqlite3.connect(r"D:\ФІТ 1-11\Андрущенко\NPC.db")
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table_name} LIMIT 0")
    columns = [description[0] for description in cursor.description]
    conn.close()
    return columns


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Ласкаво просимо до бота!\n"
                                    "Виберіть ваш тип користувача:\n"
                                    "/register_admin - Реєстрація як адмін\n"
                                    "/register_user - Реєстрація як користувач")

@bot.message_handler(commands=['register_admin'])
def register_admin(message):
    user_id = message.from_user.id
    bot.send_message(message.chat.id, "Введіть пароль для реєстрації як адміністратор:")
    bot.register_next_step_handler(message, check_password)

def check_password(message):
    user_id = message.from_user.id
    if message.text.strip() == "admin":  # Замініть на більш безпечний спосіб перевірки пароля
        user_roles[user_id] = 'admin'
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(
            telebot.types.InlineKeyboardButton("команди", callback_data='admin_commands'))
        bot.send_message(message.chat.id, "Ви зареєстровані як адміністратор.", reply_markup=markup)
        
    else:
        bot.send_message(message.chat.id, "Неправильний пароль. Спробуйте ще раз.")

@bot.message_handler(commands=['register_user'])
def register_user(message):
    user_id = message.from_user.id
    user_roles[user_id] = 'user'
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(
        telebot.types.InlineKeyboardButton("команди", callback_data='user_commands'))
    bot.send_message(message.chat.id, "Ви зареєстровані як користувач.", reply_markup=markup)
@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    if call.data == 'admin_commands':
        # Виводимо список команд для адміністратора
        bot.send_message(call.message.chat.id, "Список команд для адміністратора:\n"
                        "/get_table_names - переглянути назви таблиць \n"
                        "/select_data - отримати дані про персонажа \n"
                        "/get_names - отримати імена персонажів \n"
                        "/add_npc - додати песонажа \n"
                        "/delete_npc - видалити персонажа \n"
                        "/update_npc - змінити дані про персонажа \n")
    elif call.data == 'user_commands':
        # Виводимо список команд для користувача
        bot.send_message(call.message.chat.id, "Список команд для користувача:\n"
            "/get_table_names - переглянути назви таблиць \n"
            "/select_data - отримати дані про персонажа \n"
            "/get_names - отримати імена персонажів \n")


@bot.message_handler(commands=['get_table_names'])          #table names
def table_names_command(message):
    tables = table_names()
    result = f"Таблиці в базі даних: {', '.join(tables)}"
    bot.send_message(message.chat.id, result)


@bot.message_handler(commands=['get_names'])                 #get names 
def get_names_command(message):
    bot.send_message(message.chat.id, "Введіть назву таблиці для отримання імен персонажів:")
    bot.register_next_step_handler(message, process_get_names)
def process_get_names(message):
    table_name = message.text.strip()
    if table_name not in table_names():
        bot.send_message(message.chat.id, "Таблиця не знайдена.")
        return
    names = select_data(table_name, columns='Name')  
    result = '\n'.join([row[0] for row in names])
    bot.send_message(message.chat.id, f"Імена персонажів у таблиці {table_name}:\n{result}")


@bot.message_handler(commands=['select_data'])               #select data 
def select_data_command(message):
    msg = bot.send_message(message.chat.id, "Введіть назву таблиці (NPCs, Skills):")
    bot.register_next_step_handler(msg, process_table_name)

def process_table_name(message):
    table_name = message.text.strip()
    msg = bot.send_message(message.chat.id, "Введіть назву стовбця (або * для всіх):")
    bot.register_next_step_handler(msg, process_columns, table_name)

def process_columns(message, table_name):
    columns = message.text.strip()
    names = select_data(table_name, columns='Name')  # Отримати лише імена
    msg = bot.send_message(message.chat.id, f"Введіть iмя персонажу ({names}):")
    bot.register_next_step_handler(msg, process_where, table_name, columns)  

def process_where(message, table_name, columns):
    name = message.text.strip()
    where = f"Name='{name}'"  # Створити умову where
    results = select_data(table_name, columns, where=where)
    response = "\n".join([str(row) for row in results]) if results else "Немає результатів."
    bot.send_message(message.chat.id, response)


@bot.message_handler(commands=['add_npc'])                  #add character 
def add_npc_command(message):
    msg=bot.send_message(message.chat.id, "Введіть назву таблиці")
    bot.register_next_step_handler(msg, process_table1)           
def process_table1(message):
    table_name=message.text.strip()
    columns=get_column_names(table_name)
    msg=bot.send_message(message.chat.id, f"Введіть дані про вашого персонажа в послідовності: {columns}")
    bot.register_next_step_handler(msg, lambda m: process_data(m, table_name, columns))          
def process_data(message, table_name, columns):
    new_data = message.text.strip().split(',')  # Розділяємо введені дані
    
    # Перевіряємо, чи кількість даних відповідає кількості колонок
    if len(new_data) != len(columns):
        bot.send_message(message.chat.id, "Кількість введених даних не відповідає кількості колонок.")
        return

    # Перетворюємо дані на кортеж
    new_data_tuple = tuple(new_data)

    try_count = 0
    success = False
    while try_count < 5 and not success:
        try:
            conn = sqlite3.connect(r"D:\ФІТ 1-11\Андрущенко\NPC.db")
            cursor = conn.cursor()

            if table_name == "NPCs":
                cursor.execute("INSERT INTO NPCs (Name, Status, Age, Location, Gift, Birthday) VALUES (?, ?, ?, ?, ?, ?)", new_data_tuple)
            elif table_name == "Skills":
                cursor.execute("INSERT INTO Skills (Name, Fishing, Farming, Combat, Mining) VALUES (?, ?, ?, ?, ?)", new_data_tuple)
            else:
                bot.send_message(message.chat.id, "Таблиця не знайдена.")
                return

            conn.commit()
            bot.send_message(message.chat.id, "Персонажа успішно додано!")
            success = True
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e).lower():
                try_count += 1
                bot.send_message(message.chat.id, "База даних зайнята. Спроба додавання... Будь ласка, зачекайте.")
                time.sleep(2)  
            else:
                bot.send_message(message.chat.id, f"Сталася помилка: {str(e)}")
                break
        finally:
            conn.close()

    if not success:
        bot.send_message(message.chat.id, "Не вдалося додати персонажа. Будь ласка, спробуйте пізніше.")


@bot.message_handler(commands=['delete_npc'])      
def delete_command(message):
    msg = bot.send_message(message.chat.id, "Введіть назву таблиці (NPCs, Skills):")
    bot.register_next_step_handler(msg, process_delete_table)
def process_delete_table(message):
    table_name = message.text.strip()
    names = select_data(table_name, columns='Name')  
    msg = bot.send_message(message.chat.id, f"Введіть ім'я персонажа для видалення ({names}):")
    bot.register_next_step_handler(msg, lambda m: process_delete_data(m, table_name))
def process_delete_data(message, table_name):
    conn = sqlite3.connect(r"D:\ФІТ 1-11\Андрущенко\NPC.db")
    cursor = conn.cursor()
    name= message.text.strip()
    where = f"Name='{name}'"  # Створити умову where
    cursor.execute(f"DELETE FROM {table_name} WHERE {where}")
    conn.commit()
    conn.close()
    bot.send_message(message.chat.id, f"персонажа видалено ")


@bot.message_handler(commands=['update_npc'])
def update_npc_command(message):
    msg = bot.send_message(message.chat.id, "Введіть назву таблиці(NPCs, Skills):")
    bot.register_next_step_handler(msg, process_table_name4)

def process_table_name4(message):
    table_name = message.text.strip()
    columns=get_column_names(table_name)
    msg = bot.send_message(message.chat.id, f"Введіть назву стовбця з ({columns}):")
    bot.register_next_step_handler(msg, column_update, table_name)
def column_update(message, table_name):
    column_name=message.text.strip()
    names = select_data(table_name, columns='Name')  
    msg = bot.send_message(message.chat.id, f"Введіть ім'я персонажа ({names}):")
    bot.register_next_step_handler(msg, name_update,table_name, column_name)
def name_update(message, table_name, column_name):
    name= message.text.strip()
    msg = bot.send_message(message.chat.id, f"Введіть зміни:")
    bot.register_next_step_handler(msg, ch_update, table_name, column_name, name)
def ch_update(message, table_name, column_name, name):
    conn = sqlite3.connect(r"D:\ФІТ 1-11\Андрущенко\NPC.db")
    cursor = conn.cursor()
    new_value = message.text.strip()


    cursor.execute(f"UPDATE {table_name} SET {column_name} = ? WHERE Name = ?", (new_value, name))
    conn.commit()
    conn.close()
    bot.send_message(message.chat.id, f"Персонажа '{name}' відредаговано.")



def run_bot():
    bot.polling()  


def run_streamlit():    
    conn = sqlite3.connect(r"D:\ФІТ 1-11\Андрущенко\NPC.db") 
    npc_df = pd.read_sql("SELECT * FROM NPCs", conn)
    skills_df = pd.read_sql("SELECT * FROM Skills", conn)

    st.title('Статистика персонажів гри Stardew Valley')

    # Завантаження даних
    df = pd.merge(npc_df, skills_df, on='Name')
    # Створення вкладок
    tabs = st.tabs(["Діаграми", "База даних", "Адмін"])

                                                                    #TABS 1 
    # Вкладка для діаграм
    with tabs[0]:
        st.subheader('Кругова діаграма')

        # Вибір типу статистики
        stat_type = st.selectbox('Оберіть тип статистики:', options=['Місце проживання', 'Сімейний статус', 'День народження'])

        # Фільтрація даних та підрахунок статистики
        if stat_type == 'Місце проживання':
            filtered_npc = npc_df

            # Підрахунок статистики за місцем проживання
            location_counts = filtered_npc['Location'].value_counts()

            # Створення кругової діаграми
            fig1, ax1 = plt.subplots()
            ax1.pie(location_counts, labels=location_counts.index, autopct='%1.1f%%', startangle=90)
            ax1.axis('equal')  # Рівні пропорції для кругової діаграми
            st.pyplot(fig1)
        elif stat_type == 'День народження':
            filtered_npc = npc_df

            # Підрахунок статистики за місцем проживання
            day_counts = filtered_npc['Birthday'].value_counts()

            # Створення кругової діаграми
            fig1, ax1 = plt.subplots()
            ax1.pie(day_counts, labels=day_counts.index, autopct='%1.1f%%', startangle=90)
            ax1.axis('equal')  # Рівні пропорції для кругової діаграми
            st.pyplot(fig1)

        else:  # Якщо вибрано "Сімейний статус"

            filtered_npc = npc_df

            # Підрахунок статистики за сімейним статусом
            status_counts = filtered_npc['Status'].value_counts()

            # Створення кругової діаграми
            fig2, ax2 = plt.subplots()
            ax2.pie(status_counts, labels=status_counts.index, autopct='%1.1f%%', startangle=90)
            ax2.axis('equal')  # Рівні пропорції для кругової діаграми
            st.pyplot(fig2)

        # Лінійна діаграма з даними скілс
        st.subheader('Лінійна діаграма з даними Skills')

        # Вік персонажів - використовується для фільтрації
        age_filter = st.slider('Оберіть віковий діапазон:', min_value=0, max_value=100, value=(0, 100))
        filtered_npc_age = filtered_npc[(filtered_npc['Age'] >= age_filter[0]) & (filtered_npc['Age'] <= age_filter[1])]

        # Фільтрація скілс за віком персонажів
        filtered_skills = skills_df[skills_df['Name'].isin(filtered_npc_age['Name'])]

        # Візуалізація
        if not filtered_npc_age.empty and not filtered_skills.empty:
            plt.figure(figsize=(10, 5))

            # Створення лінійної діаграми з чотирма лініями
            num_characters = len(filtered_skills)
            x_values = range(1, num_characters + 1)  # Від 1 до кількості персонажів

            # Збережемо значення скілів у змінні
            farming_values = filtered_skills['Farming'].values
            fishing_values = filtered_skills['Fishing'].values
            combat_values = filtered_skills['Combat'].values
            mining_values = filtered_skills['Mining'].values

            # Додавання ліній на графік
            plt.plot(x_values, farming_values, marker='o', label='Farming')
            plt.plot(x_values, fishing_values, marker='o', label='Fishing')
            plt.plot(x_values, combat_values, marker='o', label='Combat')
            plt.plot(x_values, mining_values, marker='o', label='Mining')

            plt.title('Навички персонажів')
            plt.xlabel('Кількість персонажів')  # Вісь X - кількість персонажів
            plt.ylabel('Оцінка скілс')  # Вісь Y - рівень скілс

            # Встановлюємо межі осі Y від 1 до 10
            plt.ylim(1, 10)

            # Встановлюємо підписи для осі X
            plt.xticks(x_values)  # Відображення кількості персонажів
            plt.legend()  # Додавання легенди
            st.pyplot(plt)
        else:
            st.write("Немає даних для вибраного вікового діапазону або скілс.")

                                                                                    # TABS 2
    with tabs[1]:
        st.subheader('Фільтри для таблиці NPCs')

        # Створення фільтрів
        status_filter = st.multiselect('Сімейний стан', npc_df['Status'].unique())
        location_filter = st.multiselect('Місце проживання', npc_df['Location'].unique())
        age_filter = st.slider('Вік', int(npc_df['Age'].min()), int(npc_df['Age'].max()), (int(npc_df['Age'].min()), int(npc_df['Age'].max())))

        # Фільтрація даних
        # Фільтр по сімейному статусу
        if status_filter:
            filtered_npc_df = npc_df[npc_df['Status'].isin(status_filter)]
        else:
            filtered_npc_df = npc_df
        
        # Фільтр по місцю проживання
        if location_filter:
            filtered_npc_df = filtered_npc_df[filtered_npc_df['Location'].isin(location_filter)]

        # Фільтр по віку
        filtered_npc_df = filtered_npc_df[(filtered_npc_df['Age'] >= age_filter[0]) & (filtered_npc_df['Age'] <= age_filter[1])]

        # Фільтрація таблиці skills
        filtered_skills_df = skills_df[skills_df['Name'].isin(filtered_npc_df['Name'])]

        # Відображення відфільтрованих даних
        st.subheader('Таблиця NPCs')
        st.dataframe(filtered_npc_df)

        st.subheader('Таблиця Skills')
        st.dataframe(filtered_skills_df)
    with tabs[2]:
        st.subheader("Вхід адміністратора")

        # Створення форми для введення пароля
        admin_password = st.text_input("Введіть пароль", type="password")
        
        # Перевірка правильності пароля
        if admin_password == "admin":
            st.success("Вхід успішний! Ви у режимі адміністратора.")
            
            # Адмін-функції: додавання або редагування персонажів
            st.subheader("Адмін-функції")

            # Вибір персонажа для редагування або додавання нового
            selected_act = st.selectbox("Оберіть дію", ["Додати нового", "Редагувати існуючого", "Видалити персонажа"])
                                                                        #NEW
            if selected_act=="Додати нового":
                selected_table = st.selectbox("Оберіть таблицю",["NPCs","Skills","Обидві таблиці"])
                if selected_table=="NPCs":
                    new_name = st.text_input("Введіть ім'я персонажа")
                    new_age=st.text_input("Введіть вік персонажа")
                    new_status = st.selectbox("Оберіть статус",["Single","Married"])
                    new_location = st.selectbox("Оберіть місцепроживання",["Town","Mountains", "Desert", "Island"])
                    new_gift = st.text_input("Введіть улюблений  подарунок")
                    new_birthday = st.selectbox("Оберіть день народження ",["Fall","Spring", "Summer", "Winter"])
                    
                    if st.button("Додати персонажа"):
                        conn.execute("INSERT INTO NPCs (Name, Status, Age, Location, Gift, Birthday) VALUES (?, ?, ?, ?, ?, ?)", (new_name, new_status,new_age, new_location, new_gift, new_birthday))

                        conn.commit()
                        st.success("Персонажа додано")

                elif selected_table=="Skills":
                    new_name = st.text_input("Введіть ім'я персонажа")
                    new_fishing= st.text_input("Введіть рівень навички Fishing")
                    new_farming= st.text_input("Введіть рівень навички Farming")
                    new_combat= st.text_input("Введіть рівень навички Combat")
                    new_mining= st.text_input("Введіть рівень навички Mining")
                    if st.button("Додати персонажа"):
                        conn.execute("INSERT INTO Skills (Name, Fishing, Farming, Combat, Mining) VALUES (?, ?, ?, ?, ?)", 
                                (new_name, new_fishing, new_farming, new_combat, new_mining))
                        conn.commit()
                        st.success("Персонажа додано")
                else:
                    new_name = st.text_input("Введіть ім'я персонажа")
                    new_age=st.text_input("Введіть вік персонажа")
                    new_status = st.selectbox("Оберіть статус",["Single","Married"])
                    new_location = st.selectbox("Оберіть місцепроживання",["Town","Mountains", "Desert", "Island"])
                    new_gift = st.text_input("Введіть улюблений  подарунок")
                    new_birthday = st.selectbox("Оберіть день народження ",["Fall","Spring", "Summer", "Winter"])
                    new_fishing= st.text_input("Введіть рівень навички Fishing")
                    new_farming= st.text_input("Введіть рівень навички Farming")
                    new_combat= st.text_input("Введіть рівень навички Combat")
                    new_mining= st.text_input("Введіть рівень навички Mining")
                    if st.button("Додати персонажа"):
                        conn.execute("INSERT INTO NPCs (Name, Status, Age, Location, Gift, Birthday) VALUES (?, ?, ?, ?, ?, ?)", (new_name, new_status,new_age, new_location, new_gift, new_birthday))
                        conn.execute("INSERT INTO Skills (Name, Fishing, Farming, Combat, Mining) VALUES (?, ?, ?, ?, ?)", 
                                (new_name, new_fishing, new_farming, new_combat, new_mining))                               
                        conn.commit()
                        st.success("Персонажа додано")
            elif selected_act=="Видалити персонажа":
                selected_table = st.selectbox("Оберіть таблицю",["NPCs","Skills","Обидві таблиці"])
                selected_character = st.selectbox("Оберіть персонажа", npc_df['Name'].unique())
                if st.button("видалити персонажа"):
                    if selected_table=="Обидві таблиці":
                        conn.execute(f"DELETE FROM NPCs WHERE Name='{selected_character}'")
                        conn.execute(f"DELETE FROM Skills WHERE Name='{selected_character}'")
                        conn.commit()
                        st.success("Персонажа видалено")

                    else:
                        conn.execute(f"DELETE FROM {selected_table} WHERE Name={selected_character}")  
                        conn.commit()  
                        st.success("Персонажа видалено")
                                                            # EDIT                 
            else:
                #  редагування  персонажа

                selected_table = st.selectbox("Оберіть таблицю",["NPCs","Skills"])
                if selected_table=="NPCs":
                    selected_character = st.selectbox("Оберіть персонажа", npc_df['Name'].unique())
                    selected_column=st.selectbox("Оберіть дaні для зміни:",["Name","Status","Age","Location","Gift","Birthday"] )
                    if selected_column=="Name":
                        new_data=st.text_input("Введіть ім'я персонажа")
                    elif selected_column=="Status":
                        new_data=st.selectbox("Оберіть статус",["Single","Married"])
                    elif selected_column=="Location":
                        new_data = st.selectbox("Оберіть місцепроживання",["Town","Mountains", "Desert","Island"])
                    elif selected_column=="Age":
                        new_data=st.text_input("Введіть вік персонажа")
                    elif selected_column=="Gift":
                        new_data=st.text_input("Введіть улюблений подарунок персонажа")
                    else:
                        new_birthday = st.selectbox("Оберіть день народження",["Fall","Spring", "Summer", "Winter"])
                else:
                    selected_character = st.selectbox("Оберіть персонажа", npc_df['Name'].unique())
                    selected_column=st.selectbox("Оберіть дaні для зміни:",["Farming","Fishing","Mining","Combat"] )
                    if selected_column=="Farming":
                        new_farming= st.text_input("Введіть рівень навички Farming")
                    elif selected_column=="Fishing":
                        new_fishing= st.text_input("Введіть рівень навички Fishing")
                    elif selected_column=="Combat":
                        new_combat= st.text_input("Введіть рівень навички Combat")
                    else:
                        new_mining= st.text_input("Введіть рівень навички Mining")
                    
                    
                if st.button("Зберегти зміни"):
                    if selected_table == "NPCs":
                        conn.execute(f"UPDATE NPCs SET {selected_column} = ? WHERE Name = ?", (new_data, selected_character))
                    else:
                        conn.execute(f"UPDATE Skills SET {selected_column} = ? WHERE Name = ?", (new_data, selected_character))
                    conn.commit()
                st.success(f"Персонаж {selected_character} успішно оновлений!")
        else:
            st.error("Неправильний пароль. Спробуйте ще раз.")
if __name__ == "__main__":
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.start()

    streamlit_thread = threading.Thread(target=run_streamlit)
    streamlit_thread.start()