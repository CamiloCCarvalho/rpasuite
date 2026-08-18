(function () {
    "use strict";

    const CHART_COLORS = {
        text: "#e6e9ef",
        muted: "#8892a3",
        grid: "rgba(255,255,255,0.06)",
        completed: "#2fb37c",
        failed: "#e5484d",
        interrupted: "#ff2d55",
        running: "#4f8cff",
        total: "#7c5cff",
        success: "#2fb37c",
        skipped: "#8892a3",
        pending: "#d99b2f",
        queued: "#d99b2f",
        processing: "#4f8cff",
        retrying: "#d99b2f",
        cancelled: "#8892a3",
        debug: "#8892a3",
        info: "#4f8cff",
        warning: "#d99b2f",
        error: "#e5484d",
        critical: "#ff2d55",
    };

    function pickColor(name) {
        return CHART_COLORS[name] || "#4f8cff";
    }

    async function fetchJSON(url) {
        const res = await fetch(url, { headers: { Accept: "application/json" } });
        if (!res.ok) throw new Error("Request failed: " + res.status);
        return await res.json();
    }

    function baseAxisOptions() {
        return {
            ticks: { color: CHART_COLORS.muted },
            grid: { color: CHART_COLORS.grid },
        };
    }

    function makeLineChart(ctx, data) {
        const labels = data.map((r) => r.date);
        return new Chart(ctx, {
            type: "line",
            data: {
                labels,
                datasets: [
                    {
                        label: "Total",
                        data: data.map((r) => r.total),
                        borderColor: CHART_COLORS.total,
                        backgroundColor: "rgba(124,92,255,0.15)",
                        tension: 0.3,
                        fill: true,
                    },
                    {
                        label: "Completed",
                        data: data.map((r) => r.completed),
                        borderColor: CHART_COLORS.completed,
                        backgroundColor: "rgba(47,179,124,0.10)",
                        tension: 0.3,
                    },
                    {
                        label: "Failed",
                        data: data.map((r) => r.failed),
                        borderColor: CHART_COLORS.failed,
                        backgroundColor: "rgba(229,72,77,0.10)",
                        tension: 0.3,
                    },
                    {
                        label: "Interrupted",
                        data: data.map((r) => r.interrupted),
                        borderColor: CHART_COLORS.interrupted,
                        backgroundColor: "rgba(255,45,85,0.10)",
                        tension: 0.3,
                    },
                ],
            },
            options: {
                maintainAspectRatio: false,
                plugins: {
                    legend: { labels: { color: CHART_COLORS.text } },
                    tooltip: { intersect: false, mode: "index" },
                },
                scales: {
                    x: baseAxisOptions(),
                    y: Object.assign(baseAxisOptions(), { beginAtZero: true }),
                },
            },
        });
    }

    function makeDoughnut(ctx, data, labelKey, valueKey) {
        const labels = data.map((r) => r[labelKey]);
        const values = data.map((r) => r[valueKey]);
        const colors = labels.map((n) => pickColor(n));
        return new Chart(ctx, {
            type: "doughnut",
            data: {
                labels,
                datasets: [
                    {
                        data: values,
                        backgroundColor: colors,
                        borderColor: "#161a22",
                        borderWidth: 2,
                    },
                ],
            },
            options: {
                maintainAspectRatio: false,
                cutout: "62%",
                plugins: {
                    legend: { position: "right", labels: { color: CHART_COLORS.text, boxWidth: 12 } },
                },
            },
        });
    }

    function makeBar(ctx, data) {
        const labels = data.map((r) => r.automation_name);
        return new Chart(ctx, {
            type: "bar",
            data: {
                labels,
                datasets: [
                    {
                        label: "Completed",
                        data: data.map((r) => r.completed),
                        backgroundColor: CHART_COLORS.completed,
                    },
                    {
                        label: "Failed",
                        data: data.map((r) => r.failed),
                        backgroundColor: CHART_COLORS.failed,
                    },
                    {
                        label: "Other",
                        data: data.map((r) => Math.max(0, (r.executions || 0) - (r.completed || 0) - (r.failed || 0))),
                        backgroundColor: CHART_COLORS.muted,
                    },
                ],
            },
            options: {
                maintainAspectRatio: false,
                plugins: { legend: { labels: { color: CHART_COLORS.text } } },
                scales: {
                    x: Object.assign(baseAxisOptions(), { stacked: true }),
                    y: Object.assign(baseAxisOptions(), { stacked: true, beginAtZero: true }),
                },
            },
        });
    }

    async function initOverview() {
        try {
            const ts = document.getElementById("chart-timeseries");
            if (ts) {
                const data = await fetchJSON("/api/executions/timeseries?days=14");
                makeLineChart(ts.getContext("2d"), data);
            }
        } catch (e) { console.warn("timeseries chart failed:", e); }

        try {
            const items = document.getElementById("chart-items");
            if (items) {
                const data = await fetchJSON("/api/items/status");
                makeDoughnut(items.getContext("2d"), data, "status", "count");
            }
        } catch (e) { console.warn("items chart failed:", e); }

        try {
            const logs = document.getElementById("chart-logs");
            if (logs) {
                const data = await fetchJSON("/api/logs/levels");
                makeDoughnut(logs.getContext("2d"), data, "log_level", "count");
            }
        } catch (e) { console.warn("logs chart failed:", e); }

        try {
            const top = document.getElementById("chart-top");
            if (top) {
                const data = await fetchJSON("/api/executions/top?limit=6");
                makeBar(top.getContext("2d"), data);
            }
        } catch (e) { console.warn("top chart failed:", e); }
    }

    function initItems() {
        document.querySelectorAll(".cell-data-toggle").forEach(function (btn) {
            btn.addEventListener("click", function (event) {
                event.preventDefault();
                event.stopPropagation();

                const wrap = btn.closest(".cell-data");
                if (!wrap) return;
                const body = wrap.querySelector(".cell-data-body");
                const fullSource = wrap.querySelector(".cell-data-full-source");
                const previewSource = wrap.querySelector(".cell-data-preview-source");
                if (!body) return;

                const expanding = !wrap.classList.contains("is-expanded");
                wrap.classList.toggle("is-expanded", expanding);
                btn.setAttribute("aria-expanded", expanding ? "true" : "false");
                btn.setAttribute("aria-label", expanding ? "Collapse data" : "Expand data");
                btn.title = expanding ? "Collapse" : "Expand";

                const preview = previewSource ? previewSource.textContent : body.textContent;
                const full = fullSource ? fullSource.textContent : preview;
                body.textContent = expanding ? full : preview;
            });
        });
    }

    document.addEventListener("DOMContentLoaded", function () {
        if (window.__DASHBOARD_INIT__ === "overview") {
            initOverview();
        }
        if (window.__DASHBOARD_INIT__ === "items") {
            initItems();
        }
    });
})();
