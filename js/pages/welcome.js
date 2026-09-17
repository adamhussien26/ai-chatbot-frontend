/**
 * ==========================================================================
 * Page Specific Logic: 01-welcome.html (صفحة الترحيب)
 * Handles welcome screen chat input bar and quick info card navigation.
 * ==========================================================================
 */

document.addEventListener('DOMContentLoaded', () => {
  initWelcomeChatBar();
  initFinanceCard();
});

/**
 * Initializes the chat input bar logic on the welcome hero screen.
 */
function initWelcomeChatBar() {
  const chatInput = document.getElementById('chatInput');
  const sendBtn = document.getElementById('sendBtn');

  if (!chatInput || !sendBtn) return;

  function handleSend() {
    const value = chatInput.value.trim();
    if (value === '') return;

    // Redirect to chat page with query param
    window.location.href = '06-chat.html?q=' + encodeURIComponent(value);
  }

  sendBtn.addEventListener('click', handleSend);
  chatInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') handleSend();
  });
}

/**
 * Initializes the finance card click handler.
 */
function initFinanceCard() {
  const financeCard = document.getElementById('financeCard');
  if (financeCard) {
    financeCard.addEventListener('click', () => {
      window.location.href = '06-chat.html?q=' + encodeURIComponent('الشؤون المالية والرسوم الدراسية');
    });
  }
}
