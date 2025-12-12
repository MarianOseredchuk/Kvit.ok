document.addEventListener("DOMContentLoaded", async function () {

    const eventsContainer = document.getElementById('event-list-results');
    const placeholder = document.getElementById('event-list-placeholder');
    const searchInput = document.querySelector('.search-bar input');
    const searchBtn = document.querySelector('.search-button');
    const filterBtn = document.querySelector('.filter-apply-btn');
    const resetBtn = document.getElementById('reset-filters-btn');
    
    let allEvents = []; 

    const date = new Date();
    let currentMonth = date.getMonth();
    let currentYear = date.getFullYear();
    const monthNames = ["Січень", "Лютий", "Березень", "Квітень", "Травень", "Червень", "Липень", "Серпень", "Вересень", "Жовтень", "Листопад", "Грудень"];
    
    function getMarkerForDate(dateStr) {
        const shapes = ["fa-circle", "fa-star", "fa-heart", "fa-cloud", "fa-lemon", "fa-bell"];
        const colors = ["#FFB7B2", "#FFDAC1", "#E2F0CB", "#B5EAD7", "#C7CEEA", "#E0BBE4"];
        let hash = 0;
        for (let i = 0; i < dateStr.length; i++) hash = dateStr.charCodeAt(i) + ((hash << 5) - hash);
        return {
            icon: shapes[Math.abs(hash) % shapes.length],
            color: colors[Math.abs(hash) % colors.length]
        };
    }

    async function fetchEvents() {
        try {
            const res = await fetch('/api/events');
            if (res.ok) {
                allEvents = await res.json();
                renderCalendar();
                renderEventsList(allEvents, "Усі події"); 
            }
        } catch (e) {
            console.error("Помилка:", e);
        }
    }

    function renderEventsList(eventsToRender, titleText) {
        eventsContainer.innerHTML = ''; 

        if (eventsToRender.length > 0) {
            placeholder.style.display = 'none';
            
            const h3 = document.createElement('h3');
            h3.className = 'day-separator';
            h3.innerText = titleText;
            eventsContainer.appendChild(h3);

            eventsToRender.forEach((ev, index) => {
                const card = document.createElement('div');
                card.className = `event-list-card glass-effect delay-${index % 3}`;
                
                const safeDesc = (ev.description || "").replace(/"/g, '&quot;');
                const safeImg = ev.image_url || "";
                let thumbHtml = '';
                if (safeImg && safeImg !== 'null') {
                    let firstImg = safeImg.includes(',') ? safeImg.split(',')[0] : safeImg;
                    let src = firstImg.includes('http') ? firstImg : `/static/uploads/${firstImg}`;
                    thumbHtml = `<img src="${src}" class="card-thumb" alt="${ev.title}">`;
                }

                card.innerHTML = `
                    ${thumbHtml}
                    <div class="event-time">${ev.time}</div>
                    <div class="event-info">
                        <h4 class="event-title">${ev.title}</h4>
                        <p class="event-meta">
                            <i class="fas fa-tag"></i> ${ev.type} | 
                            <i class="fas fa-map-marker-alt"></i> ${ev.location} |
                            <i class="fas fa-money-bill-wave"></i> ${ev.price} грн
                        </p>
                    </div>
                    
                    <div class="event-action" style="display:flex; flex-direction:column; gap:5px;">
                        <button class="main-cta-button" style="background-color: #95a5a6;"
                            onclick="openDetailsModal('${ev.id}', '${ev.title}', '${ev.time}', '${ev.location}', '${safeDesc}', '${safeImg}', '${ev.price}', '${ev.remaining_seats}')">
                            <i class="fas fa-info-circle"></i> Інфо
                        </button>

                        <button class="main-cta-button" 
                            onclick="openBookModal('${ev.id}', '${ev.title}', '${ev.price || 0}', '${ev.remaining_seats || 100}')">
                            Зареєструватись
                        </button>
                    </div>
                `;
                eventsContainer.appendChild(card);
            });
            eventsContainer.style.display = 'block';
        } else {
            placeholder.style.display = 'block';
            placeholder.querySelector('h3').innerText = "Нічого не знайдено";
            eventsContainer.style.display = 'none';
        }
    }

    function applySidebarFilters() {
        const checkedTypes = Array.from(document.querySelectorAll('input[name="type"]:checked')).map(cb => cb.value);
        const checkedLocs = Array.from(document.querySelectorAll('input[name="location"]:checked')).map(cb => cb.value);
        const timeFrom = document.getElementById('time-from').value;
        const timeTo = document.getElementById('time-to').value;
        const priceMin = document.getElementById('price-min').value;
        const priceMax = document.getElementById('price-max').value;

        const filtered = allEvents.filter(ev => {
            if (checkedTypes.length > 0 && !checkedTypes.includes(ev.type)) return false;
            if (checkedLocs.length > 0 && !checkedLocs.includes(ev.location)) return false;
            if (ev.time < timeFrom || ev.time > timeTo) return false;
            const evPrice = ev.price || 0;
            if (priceMin && evPrice < parseInt(priceMin)) return false;
            if (priceMax && evPrice > parseInt(priceMax)) return false;
            return true;
        });

        renderEventsList(filtered, "Відфільтровані події");
        document.querySelectorAll('.calendar-day').forEach(d => d.classList.remove('active'));
    }

    if (filterBtn) filterBtn.addEventListener('click', applySidebarFilters);
    if (resetBtn) resetBtn.addEventListener('click', () => {
        document.querySelectorAll('input[type="checkbox"]').forEach(cb => cb.checked = false);
        fetchEvents(); 
    });

    function renderCalendar() {
        const header = document.getElementById("current-month-year");
        if (header) header.innerText = `${monthNames[currentMonth]} ${currentYear}`;
        const grid = document.getElementById("calendar-grid");
        if (!grid) return;
        grid.innerHTML = "";

        ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Нд"].forEach(d => {
            const el = document.createElement("div");
            el.className = "day-name";
            el.innerText = d;
            grid.appendChild(el);
        });

        let firstDayIndex = new Date(currentYear, currentMonth, 1).getDay();
        let padding = firstDayIndex === 0 ? 6 : firstDayIndex - 1;
        const daysInMonth = new Date(currentYear, currentMonth + 1, 0).getDate();
        const monthString = String(currentMonth + 1).padStart(2, '0');

        for (let i = 0; i < padding; i++) grid.appendChild(document.createElement("div"));

        for (let i = 1; i <= daysInMonth; i++) {
            const dayDiv = document.createElement("div");
            dayDiv.className = "calendar-day";
            dayDiv.innerText = i;
            
            const dayString = String(i).padStart(2, '0');
            const fullDateStr = `${currentYear}-${monthString}-${dayString}`;
            
            const hasEvent = allEvents.some(e => e.date === fullDateStr);
            if (hasEvent) {
                dayDiv.classList.add("has-event");
                const m = getMarkerForDate(fullDateStr);
                const icon = document.createElement("i");
                icon.className = `fas ${m.icon} event-marker`;
                icon.style.color = m.color;
                dayDiv.appendChild(icon);
            }

            dayDiv.addEventListener('click', () => {
                document.querySelectorAll('.calendar-day').forEach(d => d.classList.remove('active'));
                dayDiv.classList.add('active');
                const dayEvents = allEvents.filter(e => e.date === fullDateStr);
                renderEventsList(dayEvents, `Події на ${fullDateStr}`);
            });
            grid.appendChild(dayDiv);
        }
    }
    const prevBtn = document.getElementById('prev-month');
    const nextBtn = document.getElementById('next-month');
    if (prevBtn) prevBtn.addEventListener('click', () => { currentMonth--; if(currentMonth<0){currentMonth=11;currentYear--} renderCalendar(); });
    if (nextBtn) nextBtn.addEventListener('click', () => { currentMonth++; if(currentMonth>11){currentMonth=0;currentYear++} renderCalendar(); });

    function performSearch() {
        const query = searchInput.value.toLowerCase().trim();
        if (!query) return;
        const searchResults = allEvents.filter(event => 
            event.title.toLowerCase().includes(query) || event.location.toLowerCase().includes(query)
        );
        renderEventsList(searchResults, `Результати пошуку: "${query}"`);
    }
    if(searchBtn) searchBtn.addEventListener('click', performSearch);
    if(searchInput) searchInput.addEventListener('keyup', (e) => { if(e.key==='Enter') performSearch(); });

    const bookModal = document.getElementById('bookTicketModal');
    window.openBookModal = function(id, title, price, seats) {
        closeDetailsModal();
        document.getElementById('event-id-input').value = id;
        document.getElementById('event-name-display').innerText = title;
        document.getElementById('event-price-display').innerText = price + " грн";
        document.getElementById('event-remaining-display').innerText = seats;
        bookModal.style.display = 'flex';
    }
    window.closeBookModal = function() { bookModal.style.display = 'none'; }
    
    const detailsModal = document.getElementById('eventDetailsModal');

    window.openDetailsModal = function(id, title, time, location, description, imageUrl, price, seats) {
        document.getElementById('details-title').innerText = title;
        document.getElementById('details-time').innerText = time;
        document.getElementById('details-location').innerText = location;
        document.getElementById('details-description').innerText = description || "Опис відсутній.";

        const oldImg = document.getElementById('details-image');
        if(oldImg) oldImg.style.display = 'none'; 
        let gallery = document.getElementById('event-gallery');
        if (!gallery) {
            gallery = document.createElement('div');
            gallery.id = 'event-gallery';
            gallery.className = 'gallery-scroll'; 
            const desc = document.getElementById('details-description');
            desc.parentNode.insertBefore(gallery, desc);
        }
        gallery.innerHTML = ''; 

        if (imageUrl && imageUrl !== 'null') {
            let images = [];
            if (imageUrl.includes('http')) {
                images.push(imageUrl); 
            } else {
                images = imageUrl.split(',').map(f => `/static/uploads/${f}`);
            }

            images.forEach(src => {
                if(!src) return;
                const img = document.createElement('img');
                img.src = src;
                img.className = 'gallery-item'; 
                gallery.appendChild(img);
            });
            gallery.style.display = 'flex';
        } else {
            gallery.style.display = 'none';
        }

        const detailsBtn = document.getElementById('details-book-btn');
        detailsBtn.onclick = function() { openBookModal(id, title, price, seats); };
        detailsModal.style.display = 'flex';
    }

    window.closeDetailsModal = function() { detailsModal.style.display = 'none'; }

    window.onclick = function(event) {
        if (event.target == bookModal) closeBookModal();
        if (event.target == detailsModal) closeDetailsModal();
    }

    const bookForm = document.getElementById('book-ticket-form');
    if(bookForm) {
        bookForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const eventId = document.getElementById('event-id-input').value;
            const btn = bookForm.querySelector('button[type="submit"]');
            
            btn.innerText = "Обробка...";
            btn.disabled = true;
            try {
                const response = await fetch('/api/book_ticket', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ event_id: eventId })
                });
                const result = await response.json();
                if(result.success) {
                    closeBookModal();
                    if (typeof showSuccessModal === 'function') {
                        showSuccessModal("Успіх!", "Квиток заброньовано!", () => location.reload());
                    } else {
                        alert("Вітаємо! Квиток заброньовано.");
                        location.reload();
                    }
                } else {
                    alert(result.message);
                }
            } catch(err) {
                console.error(err);
                alert("Помилка з'єднання");
            } finally {
                btn.innerText = "Підтвердити реєстрацію";
                btn.disabled = false;
            }
        });
    }

    fetchEvents();
});
