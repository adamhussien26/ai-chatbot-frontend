/**
 * ==========================================================================
 * Page Specific Logic: 06-chat.html (صفحة المحادثة والذكاء الاصطناعي)
 * Handles interactive message sending, typing indicator simulation,
 * suggestion chips, search filtering, history items, and mobile drawer.
 * ==========================================================================
 */

document.addEventListener('DOMContentLoaded', () => {
  initChatComposer();
  initSuggestionChips();
  initHistorySearch();
  initHistoryActions();
  initMobileSidebarDrawer();
  checkURLQueryParam();
});

/**
 * Knowledge Base for Smart Assistant Responses
 */
const knowledgeBase = {
  'التسجيل': 'يمكنك التسجيل في المقررات عبر البوابة الإلكترونية > الأكاديمية > تسجيل المقررات. فترة التسجيل متاحة حتى بداية الأسبوع المقبل.',
  'الرسوم': 'يمكنك سداد الرسوم الدراسية عن طريق التطبيقات البنكية (بنكك، فوري، أو عبر الخزينة المركزية). آخر موعد لسداد القسط الأول هو نهاية الشهر الجاري.',
  'المالية': 'يمكنك الاطلاع على كافة الفواتير وطرق السداد والمنح الدراسية عبر قسم الشؤون المالية بالبوابة الإلكترونية.',
  'الامتحانات': 'جدول الامتحانات النهائية ينشر رسمياً عبر موقع الكلية وقناة التليجرام الرسمية قبل أسبوعين من بدء الامتحانات.',
  'الشهادات': 'لاستخراج إفادة التخرج أو كشف الدرجات، يرجى تقديم طلب عبر مكتب شؤون الطلاب مع إرفاق خلو الطرف وإيصال السداد.'
};

/**
 * Initializes Chat Input & Messaging Engine
 */
function initChatComposer() {
  const chatInput = document.getElementById('chatInput');
  const sendBtn = document.getElementById('sendBtn');
  const messagesContainer = document.getElementById('messagesContainer');
  const typingIndicator = document.getElementById('typingIndicator');

  if (!chatInput || !sendBtn || !messagesContainer) return;

  function handleSendMessage(textQuery) {
    const text = textQuery || chatInput.value.trim();
    if (text === '') return;

    const timeStr = getCurrentTimeString();

    // 1. Append User Message Bubble
    appendUserMessage(messagesContainer, text, timeStr);

    // Clear input
    chatInput.value = '';

    // Scroll to bottom
    scrollToBottom(messagesContainer);

    // 2. Show Typing Indicator
    if (typingIndicator) {
      typingIndicator.classList.remove('hidden');
      messagesContainer.appendChild(typingIndicator);
      scrollToBottom(messagesContainer);
    }

    // 3. Simulate AI Bot Reply after 1 second
    setTimeout(() => {
      if (typingIndicator) {
        typingIndicator.classList.add('hidden');
      }

      const botReplyText = generateBotReply(text);
      appendBotMessage(messagesContainer, botReplyText, getCurrentTimeString());
      scrollToBottom(messagesContainer);
    }, 1000);
  }

  sendBtn.addEventListener('click', () => handleSendMessage());
  chatInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') handleSendMessage();
  });

  // Export to window so chips & url params can trigger it
  window.sendAssistantQuery = handleSendMessage;
}

/**
 * Checks URL query string (e.g. ?q=...) and auto-sends query if present.
 */
function checkURLQueryParam() {
  const urlParams = new URLSearchParams(window.location.search);
  const initialQuery = urlParams.get('q');
  if (initialQuery && window.sendAssistantQuery) {
    setTimeout(() => {
      window.sendAssistantQuery(initialQuery);
    }, 400);
  }
}

/**
 * Appends User Message element to the container.
 */
function appendUserMessage(container, text, timeStr) {
  const group = document.createElement('div');
  group.className = 'message-group user';
  group.innerHTML = `
    <div class="msg-row" style="flex-direction: row-reverse;">
      <div class="msg-bubble msg-bubble--user">${escapeHTML(text)}</div>
    </div>
    <div class="msg-time" style="margin-right: 0; margin-left: 0; text-align: left;">${timeStr}</div>
  `;
  container.appendChild(group);
}

/**
 * Appends Bot Message element to the container.
 */
function appendBotMessage(container, text, timeStr) {
  const group = document.createElement('div');
  group.className = 'message-group bot';
  group.innerHTML = `
    <div class="msg-row">
      <div class="msg-bubble">${text}</div>
      <img class="msg-icon" src="assets/logo.png" alt="المساعد الذكي">
    </div>
    <div class="msg-time">${timeStr}</div>
  `;
  container.appendChild(group);
}

/**
 * Generates response based on query keywords or defaults.
 */
function generateBotReply(query) {
  for (const [key, answer] of Object.entries(knowledgeBase)) {
    if (query.includes(key)) return answer;
  }
  return `تم استلام استفسارك حول: "${escapeHTML(query)}". يمكنك متابعة المزيد من التفاصيل عبر البوابة الأكاديمية أو التواصل مباشرة مع شؤون الطلاب.`;
}

/**
 * Initializes Quick Suggestion Chips listeners.
 */
function initSuggestionChips() {
  const chipButtons = document.querySelectorAll('.chip-btn');
  chipButtons.forEach((chip) => {
    chip.addEventListener('click', () => {
      const query = chip.dataset.query;
      if (query && window.sendAssistantQuery) {
        window.sendAssistantQuery(query);
      }
    });
  });
}

/**
 * Filters the history items based on search input.
 */
function initHistorySearch() {
  const searchInput = document.getElementById('historySearchInput');
  if (!searchInput) return;

  searchInput.addEventListener('input', (e) => {
    const query = e.target.value.toLowerCase().trim();
    const items = document.querySelectorAll('.history-item');

    items.forEach((item) => {
      const title = item.querySelector('.h-title')?.textContent.toLowerCase() || '';
      const snippet = item.querySelector('.h-snippet')?.textContent.toLowerCase() || '';

      if (title.includes(query) || snippet.includes(query)) {
        item.style.display = 'flex';
      } else {
        item.style.display = 'none';
      }
    });
  });
}

/**
 * Handles click selection, rename, delete, and new chat actions.
 */
function initHistoryActions() {
  const historyItems = document.querySelectorAll('.history-item');

  historyItems.forEach((item) => {
    item.addEventListener('click', (e) => {
      if (e.target.closest('.history-actions')) return;
      historyItems.forEach((i) => i.classList.remove('active'));
      item.classList.add('active');
    });

    const renameBtn = item.querySelector('.history-actions button:first-child');
    const deleteBtn = item.querySelector('.history-actions button.del');

    if (renameBtn) {
      renameBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        const titleEl = item.querySelector('.h-title');
        if (!titleEl) return;
        const newTitle = prompt('أدخل الاسم الجديد للمحادثة:', titleEl.textContent);
        if (newTitle && newTitle.trim() !== '') {
          titleEl.textContent = newTitle.trim();
        }
      });
    }

    if (deleteBtn) {
      deleteBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        if (confirm('هل أنت تأكد من رغبتك في حذف هذه المحادثة؟')) {
          item.remove();
        }
      });
    }
  });

  const newChatBtn = document.getElementById('newChatBtn');
  if (newChatBtn) {
    newChatBtn.addEventListener('click', () => {
      const messagesContainer = document.getElementById('messagesContainer');
      if (messagesContainer) {
        messagesContainer.innerHTML = `
          <div class="message-group bot">
            <div class="msg-row">
              <div class="msg-bubble">
                أهلاً بك في محادثة جديدة! 👋<br>كيف يمكنني مساعدتك الآن؟
              </div>
              <img class="msg-icon" src="assets/logo.png" alt="المساعد الذكي">
            </div>
            <div class="msg-time">${getCurrentTimeString()}</div>
          </div>
        `;
      }
    });
  }
}

/**
 * Mobile Drawer Sidebar Toggle Logic
 */
function initMobileSidebarDrawer() {
  const sidebarToggle = document.getElementById('sidebarToggle');
  const closeSidebarBtn = document.getElementById('closeSidebarBtn');
  const chatSidebar = document.getElementById('chatSidebar');
  const sidebarBackdrop = document.getElementById('sidebarBackdrop');

  if (!sidebarToggle || !chatSidebar || !sidebarBackdrop) return;

  function openDrawer() {
    chatSidebar.classList.add('mobile-open');
    sidebarBackdrop.classList.add('active');
  }

  function closeDrawer() {
    chatSidebar.classList.remove('mobile-open');
    sidebarBackdrop.classList.remove('active');
  }

  sidebarToggle.addEventListener('click', openDrawer);
  sidebarBackdrop.addEventListener('click', closeDrawer);
  if (closeSidebarBtn) closeSidebarBtn.addEventListener('click', closeDrawer);
}

/**
 * Scrolls container to bottom smoothly.
 */
function scrollToBottom(container) {
  if (container) {
    container.scrollTop = container.scrollHeight;
  }
}

/**
 * Returns formatted Arabic time string (e.g. "10:45 صباحاً").
 */
function getCurrentTimeString() {
  return new Date().toLocaleTimeString('ar-SD', { hour: '2-digit', minute: '2-digit' });
}

/**
 * HTML Escaper
 */
function escapeHTML(str) {
  return str.replace(/[&<>'"]/g, 
    tag => ({
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      "'": '&#39;',
      '"': '&quot;'
    }[tag] || tag)
  );
}
