# python -m streamlit run app.py
# streamlit run app.py

import streamlit as st
import os
from datetime import datetime

from crewai import Agent, Crew, Task, LLM, Process

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_MODEL = "openai/gpt-4o-mini"

def get_api_key():
    try:
        return st.secrets["OPENROUTER_API_KEY"]
    except Exception:
        return os.getenv("OPENROUTER_API_KEY", "")

def create_llm(api_key, model, temperature):
    return LLM(
        model=model,
        base_url=OPENROUTER_BASE_URL,
        api_key=api_key,
        temperature=temperature,
        timeout=120
    )

def create_agent(role, goal, backstory, llm):
    return Agent(
        role=role,
        goal=goal,
        backstory=backstory,
        llm=llm,
        verbose=True,
        allow_delegation=False
    )

def check_acceptance_criteria(result):
    """Перевірка виконання Acceptance Criteria з ТЗ"""
    criteria = {
        "🔍 Портрет ідеального клієнта": "портрет" in result.lower() or "ідеальн" in result.lower(),
        "🏢 Типові компанії": "компан" in result.lower() or "галуз" in result.lower(),
        "👤 Хто ухвалює рішення": "ухвал" in result.lower() or "рішен" in result.lower() or "особ" in result.lower(),
        "💡 Проблеми й потреби": "проблем" in result.lower() or "потреб" in result.lower() or "болю" in result.lower(),
        "✅ Причини купівлі": "причин" in result.lower() or "купівл" in result.lower(),
        "📊 Канали пошуку": "канал" in result.lower() or "пошук" in result.lower(),
        "📧 LinkedIn": "linkedin" in result.lower(),
        "📧 Email": "email" in result.lower() or "e-mail" in result.lower(),
        "📝 Повідомлення": "повідомлен" in result.lower() or "текст" in result.lower(),
        "📋 Оцінювання клієнтів": "оцінюван" in result.lower() or "критер" in result.lower(),
        "📊 Метрики успіху": "метрик" in result.lower() or "kpi" in result.lower() or "показник" in result.lower(),
        "🎯 Практичний план": "план" in result.lower() or "стратег" in result.lower(),
    }
    
    passed = sum(criteria.values())
    total = len(criteria)
    percentage = int(passed / total * 100)
    
    return passed, total, percentage, criteria

def build_crew(product_description, llm):
       
    icp_researcher = create_agent(
        role='Дослідник клієнтів',
        goal='Визначити портрет ідеального клієнта для B2B-продукту.',
        backstory=(
            'Ви досліджуєте потенційних клієнтів і перетворюєте опис продукту на зрозумілий портрет: '
            'тип компанії, відповідальні працівники, проблеми, потреби та причини придбати продукт.'
        ),
        llm=llm
    )
    
    
    lead_planner = create_agent(
        role='Фахівець із пошуку клієнтів',
        goal='Підібрати ефективні канали пошуку потенційних клієнтів.',
        backstory=(
            'Ви плануєте пошук клієнтів. Ви враховуєте, наскільки клієнт підходить продукту, '
            'доступність каналів, вартість контакту та конкретні дії для першого звернення.'
        ),
        llm=llm
    )
    
    
    outreach_writer = create_agent(
        role='Автор повідомлень',
        goal='Створити короткі повідомлення для першого звернення до потенційного клієнта.',
        backstory=(
            'Ви пишете персоналізовані повідомлення для LinkedIn та електронної пошти — '
            'коротко, конкретно й без нав\'язливого продажу.'
        ),
        llm=llm
    )
    
   
    sales_reviewer = create_agent(
        role='Фахівець з оцінювання клієнтів',
        goal='Перевірити план пошуку клієнтів на якість, практичність і можливі ризики.',
        backstory=(
            'Ви перевіряєте план продажів. Ви помічаєте нечіткий портрет клієнта, невдалі канали пошуку, '
            'розмиті критерії оцінювання та ситуації, у яких команда може витратити час на клієнтів, '
            'яким продукт не підходить.'
        ),
        llm=llm
    )
    
   
    
   
    icp_task = Task(
        description=(
            f'На основі опису продукту визнач, які компанії можуть бути найкращими клієнтами.\n\n'
            f'Опис продукту: {product_description}\n\n'
            'Опиши:\n'
            '1. Галузі та розмір компаній\n'
            '2. Працівників, які ухвалюють рішення про купівлю\n'
            '3. Основні проблеми та потреби\n'
            '4. Причини придбати продукт'
        ),
        expected_output=(
            'Розділ Markdown українською з пунктами:\n'
            '## Портрет ідеального клієнта\n'
            '### Типові компанії\n'
            '### Хто ухвалює рішення\n'
            '### Проблеми й потреби\n'
            '### Причини купівлі'
        ),
        agent=icp_researcher
    )
    
    
    channels_task = Task(
        description=(
            'На основі портрета ідеального клієнта запропонуй канали пошуку потенційних клієнтів.\n\n'
            'Для кожного каналу поясни:\n'
            '1. Кого саме там шукати\n'
            '2. Як використовувати канал\n'
            '3. За яким показником оцінювати ефективність'
        ),
        expected_output=(
            'Markdown-таблиця:\n'
            '| Канал | Кого шукати | Як використовувати | Показник успіху |'
        ),
        agent=lead_planner,
        context=[icp_task]
    )
    
    
    outreach_task = Task(
        description=(
            'Підготуй короткі тексти для першого звернення до потенційного клієнта.\n\n'
            'Тексти мають бути:\n'
            '1. Конкретними\n'
            '2. Ненав\'язливими\n'
            '3. Пов\'язаними з проблемами клієнта, описаними в його портреті'
        ),
        expected_output=(
            'Розділ Markdown із готовими текстами:\n'
            '## Повідомлення в LinkedIn\n'
            '## Тема листа\n'
            '## Текст першого листа\n'
            '## Повторне повідомлення'
        ),
        agent=outreach_writer,
        context=[icp_task, channels_task]
    )
    
    
    qualification_task = Task(
        description=(
            'Визнач, як команда продажів може відрізняти перспективних клієнтів від тих, '
            'кому продукт, імовірно, не підходить.\n\n'
            'Опиши:\n'
            '1. Критерії оцінювання\n'
            '2. Ознаки зацікавленості\n'
            '3. Ризики помилкової оцінки'
        ),
        expected_output=(
            'Markdown-таблиця:\n'
            '| Критерій | Ознака перспективного клієнта | Ризик, якщо ігнорувати |'
        ),
        agent=sales_reviewer,
        context=[icp_task, channels_task, outreach_task]
    )
    
    
    final_task = Task(
        description=(
            'Збери підсумковий план пошуку та залучення клієнтів на основі попередніх результатів.\n\n'
            'План має бути:\n'
            '1. Коротким\n'
            '2. Структурованим\n'
            '3. Зручним для команди продажів'
        ),
        expected_output=(
            'Markdown із розділами:\n'
            '## Портрет ідеального клієнта\n'
            '## Канали пошуку\n'
            '## Тексти повідомлень\n'
            '## Оцінювання клієнтів\n'
            '## Показники успіху'
        ),
        agent=icp_researcher,
        context=[icp_task, channels_task, outreach_task, qualification_task]
    )
    
    
    
    return Crew(
        agents=[icp_researcher, lead_planner, outreach_writer, sales_reviewer],
        tasks=[icp_task, channels_task, outreach_task, qualification_task, final_task],
        process=Process.sequential,
        verbose=True
    )




st.set_page_config(page_title="B2B Sales Leads Generator")

st.title('B2B Sales Leads Generator')
st.caption('Багатоагентний робочий процес: Портрет клієнта → Канали пошуку → Перше звернення → Оцінка → План продажів')

with st.sidebar:
    st.header("Вхідні дані")
    
    product_description = st.text_area(
        'Опис вашого B2B-продукту або послуги',
        value='Ми розробляємо AI-рішення для автоматизації B2B продажів та лідогенерації',
        height=120,
        help='Опишіть, що ви продаєте компаніям'
    )
    
    st.divider()
    st.header("Налаштування моделі")
    
    model = st.selectbox(
        'Модель',
        [
           
            'openai/gpt-4o-mini',
           
        ],
        index=0
    )
    
    temperature = st.slider(
        'Температура',
        min_value=0.0,
        max_value=1.2,
        value=0.7,
        step=0.1,
        help='Вища температура = більш креативні результати'
    )


api_key = get_api_key()
if not api_key:
    st.warning('⚠️ Додайте OPENROUTER_API_KEY ключ у Streamlit secrets або .env')

# Кнопка запуску
if st.button('Запустити генерацію лідів', type="primary", use_container_width=True):
    if not api_key:
        st.error('❌ Будь ласка, додайте API ключ')
        st.stop()
    
    if not product_description.strip():
        st.error('❌ Будь ласка, введіть опис продукту')
        st.stop()

    try:
        with st.spinner('🧠 CrewAI аналізує та генерує план продажів... Це може зайняти 2-5 хвилин'):
            llm = create_llm(api_key, model, temperature)
            crew = build_crew(product_description, llm)
            result = crew.kickoff()
        
        st.session_state.crewai_result = str(result)
        st.session_state.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.success('✅ Генерацію успішно завершено!')
        
    except Exception as e:
        st.error(f'❌ Помилка: {str(e)}')
        st.stop()


if 'crewai_result' in st.session_state and st.session_state.crewai_result:
    st.divider()
    st.header('📄 Фінальний план продажів')
    st.caption(f'Згенеровано: {st.session_state.timestamp}')
    
    st.markdown(st.session_state.crewai_result)
    

    st.divider()
    st.header('📋 Перевірка Acceptance Criteria')
    
    passed, total, percentage, criteria = check_acceptance_criteria(st.session_state.crewai_result)
    
   
    st.progress(percentage / 100)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("✅ Виконано", f"{passed}/{total}")
    col2.metric("📊 Прогрес", f"{percentage}%")
    col3.metric("❌ Залишилось", f"{total - passed}")
    
    with st.expander("📝 Детальна перевірка кожного критерію"):
        for criterion, is_met in criteria.items():
            icon = "✅" if is_met else "❌"
            st.write(f"{icon} {criterion}")
    
    # Кнопки
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            '📥 Завантажити план продажів',
            st.session_state.crewai_result,
            file_name=f'b2b_sales_plan_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md',
            mime='text/markdown',
            use_container_width=True
        )
    
    with col2:
        if st.button('🗑️ Очистити', use_container_width=True):
            del st.session_state.crewai_result
            st.rerun()