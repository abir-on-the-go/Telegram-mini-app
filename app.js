class EarnApp {
    constructor() {
        this.tg = window.Telegram.WebApp;
        this.user = null;
        this.balance = 0;
        
        this.init();
    }

    async init() {
        this.tg.expand();
        this.tg.enableClosingConfirmation();
        
        // Get user data from Telegram
        this.user = this.tg.initDataUnsafe.user;
        
        if (this.user) {
            await this.loadUserData();
            this.renderOffers();
            this.updateUI();
        } else {
            this.showError("User data not available");
        }
    }

    async loadUserData() {
        try {
            // In a real app, you'd fetch from your backend
            const userData = await this.fetchUserData(this.user.id);
            this.balance = userData.coins || 0;
            this.updateUI();
        } catch (error) {
            console.error("Error loading user data:", error);
        }
    }

    async fetchUserData(userId) {
        // Simulate API call - replace with actual backend endpoint
        return new Promise(resolve => {
            setTimeout(() => {
                resolve({
                    coins: Math.floor(Math.random() * 100),
                    completed_offers: Math.floor(Math.random() * 10)
                });
            }, 500);
        });
    }

    renderOffers() {
        const offers = [
            { id: 1, title: "Survey", reward: 5, time: "2-3 min", url: "https://cpagrip.com/offer1" },
            { id: 2, title: "App Install", reward: 8, time: "5 min", url: "https://cpagrip.com/offer2" },
            { id: 3, title: "Sign Up", reward: 10, time: "1 min", url: "https://cpagrip.com/offer3" },
            { id: 4, title: "Watch Video", reward: 3, time: "30 sec", url: "https://cpagrip.com/offer4" }
        ];

        const offersList = document.getElementById('offers-list');
        offersList.innerHTML = offers.map(offer => `
            <div class="offer-card" onclick="app.startOffer(${offer.id})">
                <h3>${offer.title}</h3>
                <div class="offer-reward">+${offer.reward} coins</div>
                <div class="offer-time">~ ${offer.time}</div>
            </div>
        `).join('');
    }

    startOffer(offerId) {
        const offer = this.getOfferById(offerId);
        if (!offer) return;

        // Open offer in external browser
        const offerUrl = `https://yourdomain.com/webapp/offer.html?offer_id=${offerId}&user_id=${this.user.id}`;
        this.tg.openLink(offerUrl);
    }

    getOfferById(offerId) {
        const offers = [
            { id: 1, reward: 5 },
            { id: 2, reward: 8 },
            { id: 3, reward: 10 },
            { id: 4, reward: 3 }
        ];
        return offers.find(o => o.id === offerId);
    }

    updateUI() {
        document.getElementById('balance').textContent = this.balance;
        document.getElementById('total-earned').textContent = this.balance;
        document.getElementById('completed-offers').textContent = Math.floor(this.balance / 5);
    }

    showError(message) {
        alert(message);
    }
}

// Initialize the app
const app = new EarnApp();

// Handle offer completion callback
function completeOffer(offerId, reward) {
    if (app.tg.platform !== 'tdesktop' && app.tg.platform !== 'android') {
        // Send data back to bot
        app.tg.sendData(JSON.stringify({
            type: 'complete_offer',
            offer_id: offerId,
            reward: reward,
            user_id: app.user.id
        }));
        
        // Update local balance
        app.balance += reward;
        app.updateUI();
        
        alert(`🎉 You earned ${reward} coins!`);
    }
}