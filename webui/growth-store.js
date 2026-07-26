import { createStore } from "/js/AlpineStore.js";
import { callJsonApi } from "/js/api.js";
import { store as chatsStore } from "/components/sidebar/chats/chats-store.js";
import {
  toastFrontendError,
  toastFrontendSuccess,
  toastFrontendInfo,
} from "/components/notifications/notification-store.js";

const DASHBOARD_API = "/plugins/autonomous_growth_engine/dashboard";
const SETUP_API = "/plugins/autonomous_growth_engine/setup";

const model = {
  loading: false,
  busy: false,
  stats: null,
  reviewItems: [],
  currentFile: null,
  selectedFilter: "all",
  setupStatus: null,

  get contextId() {
    return chatsStore?.getSelectedChatId?.() || globalThis.getContext?.() || "";
  },

  get reviewCount() {
    return this.stats?.counts?.review ?? 0;
  },
  get pipelineCount() {
    return this.stats?.counts?.pipeline ?? 0;
  },
  get publishedCount() {
    return this.stats?.counts?.published ?? 0;
  },
  get researchCount() {
    return this.stats?.counts?.research ?? 0;
  },

  get filteredItems() {
    if (!this.selectedFilter || this.selectedFilter === "all") {
      return this.reviewItems;
    }
    return this.reviewItems.filter((item) => item.type === this.selectedFilter);
  },

  init() {
    // Auto-init when store is first referenced
  },

  async onOpen() {
    await Promise.all([this.loadStats(), this.loadReviewQueue(), this.loadSetupStatus()]);
  },

  cleanup() {
    this.currentFile = null;
  },

  async loadStats() {
    this.loading = true;
    try {
      const response = await callJsonApi(DASHBOARD_API, {
        action: "stats",
        context_id: this.contextId,
      });
      this.stats = response;
    } catch (error) {
      console.error("Failed to load stats:", error);
      toastFrontendError("Failed to load dashboard stats.", "Growth Engine");
      this.stats = null;
    } finally {
      this.loading = false;
    }
  },

  async loadReviewQueue(filter = null) {
    if (filter !== null) this.selectedFilter = filter;
    try {
      const response = await callJsonApi(DASHBOARD_API, {
        action: "review_queue",
        filter: this.selectedFilter === "all" ? "" : this.selectedFilter,
        context_id: this.contextId,
      });
      this.reviewItems = response?.items || [];
    } catch (error) {
      console.error("Failed to load review queue:", error);
      toastFrontendError("Failed to load review queue.", "Growth Engine");
      this.reviewItems = [];
    }
  },

  async loadSetupStatus() {
    try {
      const response = await callJsonApi(SETUP_API, {
        action: "status",
        context_id: this.contextId,
      });
      this.setupStatus = response;
    } catch (error) {
      console.error("Failed to load setup status:", error);
      this.setupStatus = null;
    }
  },

  async initializeEngine() {
    this.busy = true;
    try {
      const response = await callJsonApi(SETUP_API, {
        action: "initialize",
        context_id: this.contextId,
      });
      toastFrontendSuccess(response?.message || "Growth engine initialized.", "Growth Engine");
      await this.onOpen();
    } catch (error) {
      console.error("Failed to initialize:", error);
      toastFrontendError("Failed to initialize growth engine.", "Growth Engine");
    } finally {
      this.busy = false;
    }
  },

  async readFile(path) {
    if (!path) return;
    this.busy = true;
    try {
      const response = await callJsonApi(DASHBOARD_API, {
        action: "read_file",
        source_path: path,
        context_id: this.contextId,
      });
      this.currentFile = { path, content: response?.content || "" };
    } catch (error) {
      console.error("Failed to read file:", error);
      toastFrontendError("Failed to read file.", "Growth Engine");
      this.currentFile = null;
    } finally {
      this.busy = false;
    }
  },

  closeFile() {
    this.currentFile = null;
  },

  async approveFile(path) {
    if (!path) return;
    this.busy = true;
    try {
      await callJsonApi(DASHBOARD_API, {
        action: "approve",
        source_path: path,
        context_id: this.contextId,
      });
      toastFrontendSuccess("Content approved and moved to pipeline.", "Growth Engine");
      if (this.currentFile?.path === path) this.currentFile = null;
      await this.loadStats();
      await this.loadReviewQueue();
    } catch (error) {
      console.error("Failed to approve:", error);
      toastFrontendError("Failed to approve content.", "Growth Engine");
    } finally {
      this.busy = false;
    }
  },

  async rejectFile(path) {
    if (!path) return;
    this.busy = true;
    try {
      await callJsonApi(DASHBOARD_API, {
        action: "reject",
        source_path: path,
        context_id: this.contextId,
      });
      toastFrontendInfo("Content rejected and deleted.", "Growth Engine");
      if (this.currentFile?.path === path) this.currentFile = null;
      await this.loadStats();
      await this.loadReviewQueue();
    } catch (error) {
      console.error("Failed to reject:", error);
      toastFrontendError("Failed to reject content.", "Growth Engine");
    } finally {
      this.busy = false;
    }
  },

  async publishFile(path) {
    if (!path) return;
    this.busy = true;
    try {
      await callJsonApi(DASHBOARD_API, {
        action: "publish",
        source_path: path,
        context_id: this.contextId,
      });
      toastFrontendSuccess("Content published.", "Growth Engine");
      if (this.currentFile?.path === path) this.currentFile = null;
      await this.loadStats();
      await this.loadReviewQueue();
    } catch (error) {
      console.error("Failed to publish:", error);
      toastFrontendError("Failed to publish content.", "Growth Engine");
    } finally {
      this.busy = false;
    }
  },
};

export const store = createStore("growthStore", model);
