/**
 * ===== AGENDA MODULE - MAIN JAVASCRIPT =====
 * Módulo principal para la gestión de agenda/calendario en Nora AI
 * Incluye: calendario interactivo, gestión de eventos, integración Google Calendar
 */

// ===== CONFIGURACIÓN GLOBAL =====
window.AgendaConfig = {
    apiBaseUrl: '/panel_cliente/' + (window.NOMBRE_NORA || 'aura') + '/agenda/api',
    debug: true,
    autoRefresh: 300000, // 5 minutos
    maxEventsPerDay: 5,
    dateFormat: 'YYYY-MM-DD',
    timeFormat: 'HH:mm',
    locale: 'es-ES'
};

// ===== CLASE PRINCIPAL DEL CALENDARIO =====
class AgendaCalendar {
    constructor(containerId = '#agenda-container') {
        this.container = document.querySelector(containerId);
        this.currentDate = new Date();
        this.selectedDate = null;
        this.events = new Map(); // Caché de eventos por fecha
        this.isLoading = false;
        this.googleCalendar = new GoogleCalendarIntegration();
        
        this.init();
    }

    /**
     * Inicialización del calendario
     */
    async init() {
        try {
            this.setupEventListeners();
            this.setupKeyboardShortcuts();
            await this.loadEvents();
            this.render();
            this.startAutoRefresh();
            
            if (AgendaConfig.debug) {
                console.log('📅 Agenda Calendar initialized successfully');
            }
        } catch (error) {
            console.error('❌ Error initializing calendar:', error);
            this.showNotification('Error inicializando calendario', 'error');
        }
    }

    /**
     * Configurar event listeners principales
     */
    setupEventListeners() {
        // Navegación del calendario
        document.addEventListener('click', (e) => {
            if (e.target.matches('.nav-prev')) {
                this.previousMonth();
            } else if (e.target.matches('.nav-next')) {
                this.nextMonth();
            } else if (e.target.matches('.nav-today')) {
                this.goToToday();
            } else if (e.target.matches('.calendar-day')) {
                this.selectDay(e.target);
            } else if (e.target.matches('.calendar-event')) {
                this.showEventDetails(e.target.dataset.eventId);
            } else if (e.target.matches('.btn-new-event')) {
                this.showNewEventModal();
            } else if (e.target.matches('.modal-close, .modal-overlay')) {
                this.closeModals();
            }
        });

        // Formularios
        document.addEventListener('submit', (e) => {
            if (e.target.matches('#event-form')) {
                e.preventDefault();
                this.saveEvent(new FormData(e.target));
            }
        });

        // Sincronización con Google
        document.addEventListener('click', (e) => {
            if (e.target.matches('.btn-google-sync')) {
                this.googleCalendar.authenticate();
            } else if (e.target.matches('.btn-sync-now')) {
                this.syncWithGoogle();
            }
        });
    }

    /**
     * Configurar atajos de teclado
     */
    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Solo activar si no estamos en un input
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;

            switch (e.key) {
                case 'ArrowLeft':
                    if (e.ctrlKey) {
                        e.preventDefault();
                        this.previousMonth();
                    }
                    break;
                case 'ArrowRight':
                    if (e.ctrlKey) {
                        e.preventDefault();
                        this.nextMonth();
                    }
                    break;
                case 'n':
                    if (e.ctrlKey) {
                        e.preventDefault();
                        this.showNewEventModal();
                    }
                    break;
                case 'Escape':
                    this.closeModals();
                    break;
                case 't':
                    if (e.ctrlKey) {
                        e.preventDefault();
                        this.goToToday();
                    }
                    break;
            }
        });
    }

    /**
     * Cargar eventos desde la API
     */
    async loadEvents(month = null, year = null) {
        if (this.isLoading) return;
        
        this.isLoading = true;
        this.showLoadingIndicator(true);

        try {
            const targetDate = month && year ? new Date(year, month - 1) : this.currentDate;
            const startDate = new Date(targetDate.getFullYear(), targetDate.getMonth(), 1);
            const endDate = new Date(targetDate.getFullYear(), targetDate.getMonth() + 1, 0);

            const response = await fetch(`${AgendaConfig.apiBaseUrl}/eventos?` + new URLSearchParams({
                start: this.formatDate(startDate),
                end: this.formatDate(endDate)
            }));

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            
            if (data.success) {
                this.updateEventsCache(data.eventos);
                this.updateEventCounters();
            } else {
                throw new Error(data.error || 'Error desconocido');
            }

        } catch (error) {
            console.error('❌ Error loading events:', error);
            this.showNotification('Error cargando eventos: ' + error.message, 'error');
        } finally {
            this.isLoading = false;
            this.showLoadingIndicator(false);
        }
    }

    /**
     * Actualizar caché de eventos
     */
    updateEventsCache(eventos) {
        // Limpiar caché del mes actual
        const monthKey = this.getMonthKey(this.currentDate);
        
        eventos.forEach(evento => {
            const eventDate = new Date(evento.fecha_inicio);
            const dateKey = this.formatDate(eventDate);
            
            if (!this.events.has(dateKey)) {
                this.events.set(dateKey, []);
            }
            
            // Evitar duplicados
            const existingEvent = this.events.get(dateKey).find(e => e.id === evento.id);
            if (!existingEvent) {
                this.events.get(dateKey).push(evento);
            }
        });

        if (AgendaConfig.debug) {
            console.log(`📅 Events cache updated. Total cached dates: ${this.events.size}`);
        }
    }

    /**
     * Renderizar calendario completo
     */
    render() {
        if (!this.container) {
            console.error('❌ Calendar container not found');
            return;
        }

        this.container.innerHTML = this.getCalendarHTML();
        this.updateCalendarHeader();
        this.renderCalendarGrid();
        this.updateSelectedDay();
        this.updateSidebar();
    }

    /**
     * Generar HTML base del calendario
     */
    getCalendarHTML() {
        return `
            <div class="agenda-container">
                <header class="agenda-header">
                    <h1>📅 Agenda - ${window.NOMBRE_NORA || 'Nora'}</h1>
                </header>

                <main class="agenda-main">
                    <!-- Toolbar de navegación -->
                    <div class="agenda-toolbar">
                        <div class="agenda-nav">
                            <button class="nav-button nav-prev" title="Mes anterior (Ctrl+←)">
                                ← Anterior
                            </button>
                            <h2 class="current-month"></h2>
                            <button class="nav-button nav-next" title="Mes siguiente (Ctrl+→)">
                                Siguiente →
                            </button>
                            <button class="nav-button secondary nav-today" title="Ir a hoy (Ctrl+T)">
                                Hoy
                            </button>
                        </div>
                        
                        <div class="agenda-actions">
                            <button class="btn-new-event" title="Nuevo evento (Ctrl+N)">
                                ➕ Nuevo Evento
                            </button>
                            
                            <div class="sync-controls">
                                <button class="nav-button btn-google-sync">
                                    🔗 Google Calendar
                                </button>
                                <button class="nav-button secondary btn-sync-now">
                                    🔄 Sincronizar
                                </button>
                            </div>
                            
                            <div class="view-toggle">
                                <button class="active" data-view="month">Mes</button>
                                <button data-view="week">Semana</button>
                                <button data-view="day">Día</button>
                            </div>
                        </div>
                    </div>

                    <!-- Grid principal -->
                    <div class="calendar-layout">
                        <div class="calendar-main">
                            <div class="calendar-grid">
                                <div class="calendar-header">
                                    <div class="calendar-header-day">Dom</div>
                                    <div class="calendar-header-day">Lun</div>
                                    <div class="calendar-header-day">Mar</div>
                                    <div class="calendar-header-day">Mié</div>
                                    <div class="calendar-header-day">Jue</div>
                                    <div class="calendar-header-day">Vie</div>
                                    <div class="calendar-header-day">Sáb</div>
                                </div>
                                <div class="calendar-body" id="calendar-body">
                                    <!-- Días del calendario se generan aquí -->
                                </div>
                            </div>
                        </div>
                        
                        <aside class="agenda-sidebar" id="agenda-sidebar">
                            <!-- Información del día seleccionado -->
                        </aside>
                    </div>
                </main>

                <!-- Loading indicator -->
                <div class="loading-overlay hidden" id="loading-overlay">
                    <div class="loading-spinner"></div>
                    <span>Cargando...</span>
                </div>
            </div>

            <!-- Modal para crear/editar eventos -->
            <div class="modal-overlay" id="event-modal">
                <div class="modal">
                    <div class="modal-header">
                        <h3 class="modal-title">Nuevo Evento</h3>
                        <button class="modal-close">✕</button>
                    </div>
                    <div class="modal-body">
                        <form id="event-form">
                            ${this.getEventFormHTML()}
                        </form>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-outline modal-close">Cancelar</button>
                        <button type="submit" form="event-form" class="btn btn-primary">Guardar</button>
                    </div>
                </div>
            </div>

            <!-- Modal para detalles del evento -->
            <div class="modal-overlay" id="event-details-modal">
                <div class="modal">
                    <div class="modal-header">
                        <h3 class="modal-title">Detalles del Evento</h3>
                        <button class="modal-close">✕</button>
                    </div>
                    <div class="modal-body" id="event-details-content">
                        <!-- Contenido se carga dinámicamente -->
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-outline modal-close">Cerrar</button>
                        <button type="button" class="btn btn-primary" id="edit-event-btn">Editar</button>
                        <button type="button" class="btn btn-danger" id="delete-event-btn">Eliminar</button>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Generar HTML del formulario de eventos
     */
    getEventFormHTML() {
        return `
            <input type="hidden" id="event-id" name="id">
            
            <div class="form-group">
                <label class="form-label" for="event-title">Título *</label>
                <input type="text" id="event-title" name="titulo" class="form-input" required>
            </div>

            <div class="form-group">
                <label class="form-label" for="event-description">Descripción</label>
                <textarea id="event-description" name="descripcion" class="form-input form-textarea" rows="3"></textarea>
            </div>

            <div class="form-row">
                <div class="form-group">
                    <label class="form-label" for="event-date">Fecha *</label>
                    <input type="date" id="event-date" name="fecha" class="form-input" required>
                </div>
                <div class="form-group">
                    <label class="form-label" for="event-time">Hora</label>
                    <input type="time" id="event-time" name="hora" class="form-input">
                </div>
            </div>

            <div class="form-row">
                <div class="form-group">
                    <label class="form-label" for="event-type">Tipo</label>
                    <select id="event-type" name="tipo" class="form-input form-select">
                        <option value="evento">📅 Evento</option>
                        <option value="reunion">👥 Reunión</option>
                        <option value="llamada">📞 Llamada</option>
                        <option value="cita">🏥 Cita</option>
                        <option value="recordatorio">⏰ Recordatorio</option>
                        <option value="tarea">✅ Tarea</option>
                    </select>
                </div>
                <div class="form-group">
                    <label class="form-label" for="event-priority">Prioridad</label>
                    <select id="event-priority" name="prioridad" class="form-input form-select">
                        <option value="baja">🟢 Baja</option>
                        <option value="media" selected>🟡 Media</option>
                        <option value="alta">🔴 Alta</option>
                    </select>
                </div>
            </div>

            <div class="form-row">
                <div class="form-group">
                    <label class="form-label" for="event-duration">Duración (min)</label>
                    <input type="number" id="event-duration" name="duracion" class="form-input" value="60" min="15" step="15">
                </div>
                <div class="form-group">
                    <label class="form-label" for="event-location">Ubicación</label>
                    <input type="text" id="event-location" name="ubicacion" class="form-input" placeholder="Oficina, Zoom, etc.">
                </div>
            </div>

            <div class="form-group">
                <div class="form-checkbox">
                    <input type="checkbox" id="event-all-day" name="todo_dia">
                    <label for="event-all-day">Todo el día</label>
                </div>
            </div>

            <div class="form-group">
                <div class="form-checkbox">
                    <input type="checkbox" id="event-sync-google" name="sincronizar_google">
                    <label for="event-sync-google">Sincronizar con Google Calendar</label>
                </div>
            </div>

            <div class="form-group">
                <label class="form-label" for="event-reminder">Recordatorio</label>
                <select id="event-reminder" name="recordatorio" class="form-input form-select">
                    <option value="0">Sin recordatorio</option>
                    <option value="15">15 minutos antes</option>
                    <option value="30">30 minutos antes</option>
                    <option value="60">1 hora antes</option>
                    <option value="1440">1 día antes</option>
                </select>
            </div>
        `;
    }

    /**
     * Actualizar header del calendario
     */
    updateCalendarHeader() {
        const monthElement = this.container.querySelector('.current-month');
        if (monthElement) {
            const monthNames = [
                'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
            ];
            monthElement.textContent = `${monthNames[this.currentDate.getMonth()]} ${this.currentDate.getFullYear()}`;
        }
    }

    /**
     * Renderizar grid de días del calendario
     */
    renderCalendarGrid() {
        const calendarBody = this.container.querySelector('#calendar-body');
        if (!calendarBody) return;

        const year = this.currentDate.getFullYear();
        const month = this.currentDate.getMonth();
        
        // Primer día del mes y del calendario (incluyendo días del mes anterior)
        const firstDayOfMonth = new Date(year, month, 1);
        const lastDayOfMonth = new Date(year, month + 1, 0);
        const firstDayOfCalendar = new Date(firstDayOfMonth);
        firstDayOfCalendar.setDate(firstDayOfCalendar.getDate() - firstDayOfMonth.getDay());

        let calendarHTML = '';
        let currentDay = new Date(firstDayOfCalendar);

        // Generar 6 semanas (42 días)
        for (let week = 0; week < 6; week++) {
            for (let day = 0; day < 7; day++) {
                const dayNumber = currentDay.getDate();
                const isCurrentMonth = currentDay.getMonth() === month;
                const isToday = this.isToday(currentDay);
                const isSelected = this.selectedDate && this.isSameDay(currentDay, this.selectedDate);
                const dateKey = this.formatDate(currentDay);
                const dayEvents = this.events.get(dateKey) || [];

                let dayClasses = ['calendar-day'];
                if (!isCurrentMonth) dayClasses.push('other-month');
                if (isToday) dayClasses.push('today');
                if (isSelected) dayClasses.push('selected');

                calendarHTML += `
                    <div class="${dayClasses.join(' ')}" 
                         data-date="${dateKey}"
                         tabindex="0"
                         role="button"
                         aria-label="Día ${dayNumber} de ${this.getMonthName(currentDay.getMonth())}">
                        <div class="day-number">${dayNumber}</div>
                        <div class="calendar-events">
                            ${this.renderDayEvents(dayEvents)}
                        </div>
                    </div>
                `;

                currentDay.setDate(currentDay.getDate() + 1);
            }
        }

        calendarBody.innerHTML = calendarHTML;
    }

    /**
     * Renderizar eventos de un día
     */
    renderDayEvents(events) {
        if (!events || events.length === 0) return '';

        let eventsHTML = '';
        const visibleEvents = events.slice(0, AgendaConfig.maxEventsPerDay);

        visibleEvents.forEach(event => {
            const typeClass = `type-${event.tipo || 'evento'}`;
            const priorityClass = `priority-${event.prioridad || 'media'}`;
            
            eventsHTML += `
                <div class="calendar-event ${typeClass} ${priorityClass}" 
                     data-event-id="${event.id}"
                     title="${event.titulo} - ${event.hora || 'Todo el día'}">
                    ${this.getEventIcon(event.tipo)} ${event.titulo}
                </div>
            `;
        });

        // Mostrar indicador si hay más eventos
        if (events.length > AgendaConfig.maxEventsPerDay) {
            const remaining = events.length - AgendaConfig.maxEventsPerDay;
            eventsHTML += `<div class="events-more">+${remaining} más</div>`;
        }

        return eventsHTML;
    }

    /**
     * Obtener icono según tipo de evento
     */
    getEventIcon(tipo) {
        const icons = {
            evento: '📅',
            reunion: '👥',
            llamada: '📞',
            cita: '🏥',
            recordatorio: '⏰',
            tarea: '✅',
            google: '🔗'
        };
        return icons[tipo] || '📅';
    }

    /**
     * Navegación del calendario
     */
    previousMonth() {
        this.currentDate.setMonth(this.currentDate.getMonth() - 1);
        this.loadEvents();
        this.render();
    }

    nextMonth() {
        this.currentDate.setMonth(this.currentDate.getMonth() + 1);
        this.loadEvents();
        this.render();
    }

    goToToday() {
        this.currentDate = new Date();
        this.selectedDate = new Date();
        this.loadEvents();
        this.render();
    }

    /**
     * Seleccionar día del calendario
     */
    selectDay(dayElement) {
        if (!dayElement.dataset.date) return;

        // Limpiar selección anterior
        this.container.querySelectorAll('.calendar-day.selected').forEach(day => {
            day.classList.remove('selected');
        });

        // Seleccionar nuevo día
        dayElement.classList.add('selected');
        this.selectedDate = new Date(dayElement.dataset.date + 'T00:00:00');
        
        this.updateSidebar();
    }

    /**
     * Actualizar sidebar con información del día seleccionado
     */
    updateSidebar() {
        const sidebar = this.container.querySelector('#agenda-sidebar');
        if (!sidebar) return;

        const selectedDateStr = this.selectedDate ? this.formatDate(this.selectedDate) : this.formatDate(new Date());
        const dayEvents = this.events.get(selectedDateStr) || [];
        const formattedDate = this.selectedDate ? 
            this.selectedDate.toLocaleDateString('es-ES', { 
                weekday: 'long', 
                year: 'numeric', 
                month: 'long', 
                day: 'numeric' 
            }) : 'Hoy';

        sidebar.innerHTML = `
            <div class="sidebar-section">
                <h3 class="sidebar-title">${formattedDate}</h3>
                
                <div class="day-stats">
                    <div class="stat-item">
                        <span class="stat-label">Eventos:</span>
                        <span class="stat-value">${dayEvents.length}</span>
                    </div>
                </div>
            </div>

            <div class="sidebar-section">
                <h4 class="sidebar-title">Eventos del día</h4>
                
                ${dayEvents.length > 0 ? this.renderEventsList(dayEvents) : '<p class="text-gray-500">No hay eventos programados</p>'}
                
                <button class="btn btn-primary w-full mt-4 btn-new-event" style="width: 100%; margin-top: 1rem;">
                    ➕ Agregar Evento
                </button>
            </div>

            <div class="sidebar-section">
                <h4 class="sidebar-title">Estado de sincronización</h4>
                <div class="sync-status" id="sync-status">
                    <span class="loading-spinner"></span>
                    Verificando...
                </div>
            </div>
        `;

        // Actualizar estado de sincronización
        this.updateSyncStatus();
    }

    /**
     * Renderizar lista de eventos para el sidebar
     */
    renderEventsList(events) {
        if (!events || events.length === 0) return '';

        return `
            <div class="event-list">
                ${events.map(event => `
                    <div class="event-item" data-event-id="${event.id}">
                        <div class="event-time">${event.hora || 'Todo el día'}</div>
                        <div class="event-title">${this.getEventIcon(event.tipo)} ${event.titulo}</div>
                        ${event.descripcion ? `<div class="event-description">${event.descripcion}</div>` : ''}
                    </div>
                `).join('')}
            </div>
        `;
    }

    /**
     * Mostrar modal para nuevo evento
     */
    showNewEventModal() {
        const modal = this.container.querySelector('#event-modal');
        const form = modal.querySelector('#event-form');
        
        // Limpiar formulario
        form.reset();
        
        // Establecer fecha seleccionada o hoy
        const targetDate = this.selectedDate || new Date();
        form.querySelector('#event-date').value = this.formatDate(targetDate);
        
        // Actualizar título del modal
        modal.querySelector('.modal-title').textContent = 'Nuevo Evento';
        
        this.showModal(modal);
    }

    /**
     * Mostrar detalles de un evento
     */
    async showEventDetails(eventId) {
        if (!eventId) return;

        const modal = this.container.querySelector('#event-details-modal');
        const content = modal.querySelector('#event-details-content');
        
        // Mostrar loading
        content.innerHTML = `
            <div class="text-center py-4">
                <div class="loading-spinner"></div>
                <p>Cargando detalles...</p>
            </div>
        `;
        
        this.showModal(modal);

        try {
            const response = await fetch(`${AgendaConfig.apiBaseUrl}/eventos/${eventId}`);
            const data = await response.json();

            if (data.success) {
                content.innerHTML = this.getEventDetailsHTML(data.evento);
                
                // Configurar botones del modal
                const editBtn = modal.querySelector('#edit-event-btn');
                const deleteBtn = modal.querySelector('#delete-event-btn');
                
                editBtn.onclick = () => this.editEvent(data.evento);
                deleteBtn.onclick = () => this.deleteEvent(eventId);
            } else {
                throw new Error(data.error);
            }
        } catch (error) {
            content.innerHTML = `
                <div class="text-center py-4 text-red-500">
                    <p>❌ Error cargando evento: ${error.message}</p>
                </div>
            `;
        }
    }

    /**
     * Generar HTML para detalles del evento
     */
    getEventDetailsHTML(evento) {
        return `
            <div class="event-details">
                <div class="event-header">
                    <h3>${this.getEventIcon(evento.tipo)} ${evento.titulo}</h3>
                    <span class="event-priority priority-${evento.prioridad}">${evento.prioridad}</span>
                </div>

                <div class="event-info">
                    <div class="info-row">
                        <strong>📅 Fecha:</strong>
                        <span>${new Date(evento.fecha).toLocaleDateString('es-ES', { 
                            weekday: 'long', 
                            year: 'numeric', 
                            month: 'long', 
                            day: 'numeric' 
                        })}</span>
                    </div>

                    ${evento.hora ? `
                        <div class="info-row">
                            <strong>⏰ Hora:</strong>
                            <span>${evento.hora}</span>
                        </div>
                    ` : ''}

                    ${evento.duracion ? `
                        <div class="info-row">
                            <strong>⏱️ Duración:</strong>
                            <span>${evento.duracion} minutos</span>
                        </div>
                    ` : ''}

                    ${evento.ubicacion ? `
                        <div class="info-row">
                            <strong>📍 Ubicación:</strong>
                            <span>${evento.ubicacion}</span>
                        </div>
                    ` : ''}

                    ${evento.descripcion ? `
                        <div class="info-row">
                            <strong>📝 Descripción:</strong>
                            <div class="event-description">${evento.descripcion}</div>
                        </div>
                    ` : ''}

                    <div class="info-row">
                        <strong>🔗 Google Calendar:</strong>
                        <span>${evento.google_event_id ? '✅ Sincronizado' : '❌ No sincronizado'}</span>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Guardar evento (crear o actualizar)
     */
    async saveEvent(formData) {
        try {
            this.showLoadingIndicator(true);

            const eventData = {
                titulo: formData.get('titulo'),
                descripcion: formData.get('descripcion'),
                fecha: formData.get('fecha'),
                hora: formData.get('hora'),
                tipo: formData.get('tipo'),
                prioridad: formData.get('prioridad'),
                duracion: parseInt(formData.get('duracion')) || 60,
                ubicacion: formData.get('ubicacion'),
                todo_dia: formData.get('todo_dia') === 'on',
                sincronizar_google: formData.get('sincronizar_google') === 'on',
                recordatorio: parseInt(formData.get('recordatorio')) || 0
            };

            const eventId = formData.get('id');
            const isEdit = eventId && eventId !== '';
            
            const url = isEdit ? 
                `${AgendaConfig.apiBaseUrl}/eventos/${eventId}` : 
                `${AgendaConfig.apiBaseUrl}/eventos`;
            
            const method = isEdit ? 'PUT' : 'POST';

            const response = await fetch(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(eventData)
            });

            const data = await response.json();

            if (data.success) {
                this.showNotification(
                    isEdit ? 'Evento actualizado correctamente' : 'Evento creado correctamente', 
                    'success'
                );
                
                this.closeModals();
                await this.loadEvents();
                this.render();
            } else {
                throw new Error(data.error);
            }
        } catch (error) {
            console.error('❌ Error saving event:', error);
            this.showNotification('Error guardando evento: ' + error.message, 'error');
        } finally {
            this.showLoadingIndicator(false);
        }
    }

    /**
     * Editar evento existente
     */
    editEvent(evento) {
        const modal = this.container.querySelector('#event-modal');
        const form = modal.querySelector('#event-form');
        
        // Llenar formulario con datos del evento
        form.querySelector('#event-id').value = evento.id;
        form.querySelector('#event-title').value = evento.titulo;
        form.querySelector('#event-description').value = evento.descripcion || '';
        form.querySelector('#event-date').value = evento.fecha;
        form.querySelector('#event-time').value = evento.hora || '';
        form.querySelector('#event-type').value = evento.tipo;
        form.querySelector('#event-priority').value = evento.prioridad;
        form.querySelector('#event-duration').value = evento.duracion || 60;
        form.querySelector('#event-location').value = evento.ubicacion || '';
        form.querySelector('#event-all-day').checked = evento.todo_dia;
        form.querySelector('#event-sync-google').checked = evento.google_event_id !== null;
        form.querySelector('#event-reminder').value = evento.recordatorio || 0;
        
        // Actualizar título del modal
        modal.querySelector('.modal-title').textContent = 'Editar Evento';
        
        // Cerrar modal de detalles y mostrar modal de edición
        this.closeModals();
        this.showModal(modal);
    }

    /**
     * Eliminar evento
     */
    async deleteEvent(eventId) {
        if (!confirm('¿Estás seguro de que quieres eliminar este evento?')) {
            return;
        }

        try {
            this.showLoadingIndicator(true);

            const response = await fetch(`${AgendaConfig.apiBaseUrl}/eventos/${eventId}`, {
                method: 'DELETE'
            });

            const data = await response.json();

            if (data.success) {
                this.showNotification('Evento eliminado correctamente', 'success');
                this.closeModals();
                await this.loadEvents();
                this.render();
            } else {
                throw new Error(data.error);
            }
        } catch (error) {
            console.error('❌ Error deleting event:', error);
            this.showNotification('Error eliminando evento: ' + error.message, 'error');
        } finally {
            this.showLoadingIndicator(false);
        }
    }

    /**
     * Sincronizar con Google Calendar
     */
    async syncWithGoogle() {
        try {
            this.showLoadingIndicator(true);
            
            const response = await fetch(`${AgendaConfig.apiBaseUrl}/google/sync`, {
                method: 'POST'
            });

            const data = await response.json();

            if (data.success) {
                this.showNotification(`Sincronización completada: ${data.eventos_sincronizados} eventos`, 'success');
                await this.loadEvents();
                this.render();
            } else {
                throw new Error(data.error);
            }
        } catch (error) {
            console.error('❌ Error syncing with Google:', error);
            this.showNotification('Error sincronizando con Google: ' + error.message, 'error');
        } finally {
            this.showLoadingIndicator(false);
        }
    }

    /**
     * Actualizar estado de sincronización
     */
    async updateSyncStatus() {
        const statusElement = this.container.querySelector('#sync-status');
        if (!statusElement) return;

        try {
            const response = await fetch(`${AgendaConfig.apiBaseUrl}/google/status`);
            const data = await response.json();

            if (data.success) {
                const status = data.status;
                statusElement.className = `sync-status ${status.estado}`;
                statusElement.innerHTML = `
                    ${status.estado === 'synced' ? '✅' : status.estado === 'syncing' ? '⏳' : '❌'}
                    ${status.mensaje}
                `;
            } else {
                statusElement.className = 'sync-status error';
                statusElement.innerHTML = '❌ Error verificando estado';
            }
        } catch (error) {
            statusElement.className = 'sync-status error';
            statusElement.innerHTML = '❌ Sin conexión';
        }
    }

    /**
     * Mostrar/ocultar modales
     */
    showModal(modal) {
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
        
        // Focus en el primer input
        const firstInput = modal.querySelector('input:not([type="hidden"]), textarea, select');
        if (firstInput) {
            setTimeout(() => firstInput.focus(), 100);
        }
    }

    closeModals() {
        this.container.querySelectorAll('.modal-overlay').forEach(modal => {
            modal.classList.remove('active');
        });
        document.body.style.overflow = '';
    }

    /**
     * Mostrar indicador de carga
     */
    showLoadingIndicator(show) {
        const overlay = this.container.querySelector('#loading-overlay');
        if (overlay) {
            if (show) {
                overlay.classList.remove('hidden');
            } else {
                overlay.classList.add('hidden');
            }
        }
    }

    /**
     * Mostrar notificaciones
     */
    showNotification(message, type = 'info', duration = 5000) {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <div class="notification-title">${type === 'success' ? '✅' : type === 'error' ? '❌' : 'ℹ️'}</div>
            <div class="notification-message">${message}</div>
        `;

        document.body.appendChild(notification);

        // Mostrar notificación
        setTimeout(() => notification.classList.add('show'), 100);

        // Ocultar automáticamente
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => document.body.removeChild(notification), 300);
        }, duration);
    }

    /**
     * Actualizar contadores de eventos
     */
    updateEventCounters() {
        // Contar eventos por tipo y prioridad
        let totalEvents = 0;
        let eventsByType = {};
        let eventsByPriority = {};

        this.events.forEach(dayEvents => {
            dayEvents.forEach(event => {
                totalEvents++;
                eventsByType[event.tipo] = (eventsByType[event.tipo] || 0) + 1;
                eventsByPriority[event.prioridad] = (eventsByPriority[event.prioridad] || 0) + 1;
            });
        });

        if (AgendaConfig.debug) {
            console.log('📊 Event counters updated:', {
                total: totalEvents,
                byType: eventsByType,
                byPriority: eventsByPriority
            });
        }
    }

    /**
     * Auto-refresh de eventos
     */
    startAutoRefresh() {
        if (AgendaConfig.autoRefresh > 0) {
            setInterval(async () => {
                if (!this.isLoading) {
                    await this.loadEvents();
                    this.render();
                    
                    if (AgendaConfig.debug) {
                        console.log('🔄 Calendar auto-refreshed');
                    }
                }
            }, AgendaConfig.autoRefresh);
        }
    }

    // ===== MÉTODOS AUXILIARES =====

    /**
     * Formatear fecha como YYYY-MM-DD
     */
    formatDate(date) {
        return date.toISOString().split('T')[0];
    }

    /**
     * Verificar si una fecha es hoy
     */
    isToday(date) {
        const today = new Date();
        return this.isSameDay(date, today);
    }

    /**
     * Verificar si dos fechas son el mismo día
     */
    isSameDay(date1, date2) {
        return date1.getFullYear() === date2.getFullYear() &&
               date1.getMonth() === date2.getMonth() &&
               date1.getDate() === date2.getDate();
    }

    /**
     * Obtener nombre del mes
     */
    getMonthName(monthIndex) {
        const months = [
            'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
            'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
        ];
        return months[monthIndex];
    }

    /**
     * Generar clave única para un mes
     */
    getMonthKey(date) {
        return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
    }
}

// ===== INTEGRACIÓN CON GOOGLE CALENDAR =====
class GoogleCalendarIntegration {
    constructor() {
        this.isAuthenticated = false;
        this.accessToken = null;
        this.clientId = null; // Se obtiene del backend
    }

    /**
     * Autenticar con Google
     */
    async authenticate() {
        try {
            // Obtener URL de autenticación del backend
            const response = await fetch(`${AgendaConfig.apiBaseUrl}/google/auth-url`);
            const data = await response.json();

            if (data.success) {
                // Abrir ventana de autenticación
                const authWindow = window.open(
                    data.auth_url,
                    'google-auth',
                    'width=500,height=600,scrollbars=yes,resizable=yes'
                );

                // Escuchar mensaje de retorno
                const messageListener = (event) => {
                    if (event.origin !== window.location.origin) return;

                    if (event.data.type === 'google-auth-success') {
                        authWindow.close();
                        this.handleAuthSuccess(event.data.code);
                        window.removeEventListener('message', messageListener);
                    } else if (event.data.type === 'google-auth-error') {
                        authWindow.close();
                        this.handleAuthError(event.data.error);
                        window.removeEventListener('message', messageListener);
                    }
                };

                window.addEventListener('message', messageListener);
            } else {
                throw new Error(data.error);
            }
        } catch (error) {
            console.error('❌ Error starting Google auth:', error);
            agenda.showNotification('Error iniciando autenticación con Google', 'error');
        }
    }

    /**
     * Manejar éxito de autenticación
     */
    async handleAuthSuccess(authCode) {
        try {
            const response = await fetch(`${AgendaConfig.apiBaseUrl}/google/callback`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ code: authCode })
            });

            const data = await response.json();

            if (data.success) {
                this.isAuthenticated = true;
                agenda.showNotification('¡Conectado con Google Calendar!', 'success');
                agenda.updateSyncStatus();
            } else {
                throw new Error(data.error);
            }
        } catch (error) {
            console.error('❌ Error completing Google auth:', error);
            agenda.showNotification('Error completando autenticación', 'error');
        }
    }

    /**
     * Manejar error de autenticación
     */
    handleAuthError(error) {
        console.error('❌ Google auth error:', error);
        agenda.showNotification('Error en autenticación: ' + error, 'error');
    }
}

// ===== INICIALIZACIÓN GLOBAL =====
let agenda;

document.addEventListener('DOMContentLoaded', () => {
    // Verificar que estamos en la página de agenda
    if (document.querySelector('#agenda-container') || 
        window.location.pathname.includes('/agenda')) {
        
        try {
            agenda = new AgendaCalendar('#agenda-container');
            
            // Hacer disponible globalmente para debugging
            if (AgendaConfig.debug) {
                window.agenda = agenda;
                console.log('📅 Agenda module loaded successfully');
                console.log('🔧 Debug mode enabled. Access calendar via window.agenda');
            }
        } catch (error) {
            console.error('❌ Error initializing agenda:', error);
        }
    }
});

// ===== EXPORTAR PARA MÓDULOS =====
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { AgendaCalendar, GoogleCalendarIntegration };
}
