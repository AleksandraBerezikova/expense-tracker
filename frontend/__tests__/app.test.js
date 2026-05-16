const { api, formatAmount, formatDate } = require("../app.js");

describe("formatAmount", () => {
    test("formats a number as Russian rubles", () => {
        expect(formatAmount(450)).toBe("450,00\u00A0\u20BD");
    });

    test("formats a string amount", () => {
        expect(formatAmount("123.45")).toBe("123,45\u00A0\u20BD");
    });

    test("returns 0 ruble fallback for invalid input", () => {
        expect(formatAmount("not a number")).toBe("0,00\u00A0\u20BD");
    });

    test("handles zero", () => {
        expect(formatAmount(0)).toBe("0,00\u00A0\u20BD");
    });
});

describe("formatDate", () => {
    test("reformats ISO date to DD.MM.YYYY", () => {
        expect(formatDate("2025-04-05")).toBe("05.04.2025");
    });

    test("returns empty string for empty input", () => {
        expect(formatDate("")).toBe("");
        expect(formatDate(null)).toBe("");
        expect(formatDate(undefined)).toBe("");
    });
});

describe("api.buildUrl", () => {
    test("builds URL without query params", () => {
        const url = api.buildUrl("/expenses");
        expect(url).toMatch(/\/expenses$/);
    });

    test("appends query params", () => {
        const url = api.buildUrl("/expenses", { category: "food", limit: 10 });
        expect(url).toContain("category=food");
        expect(url).toContain("limit=10");
    });

    test("skips empty, null, and undefined params", () => {
        const url = api.buildUrl("/expenses", {
            category: "",
            date_from: null,
            date_to: undefined,
            limit: 5,
        });
        expect(url).not.toContain("category=");
        expect(url).not.toContain("date_from=");
        expect(url).not.toContain("date_to=");
        expect(url).toContain("limit=5");
    });
});

describe("api CRUD operations", () => {
    beforeEach(() => {
        global.fetch = jest.fn();
    });

    afterEach(() => {
        jest.resetAllMocks();
    });

    test("createExpense POSTs JSON and returns parsed body", async () => {
        const fakeExpense = { id: "abc", amount: 450, category: "food" };
        fetch.mockResolvedValue({
            ok: true,
            json: async () => fakeExpense,
        });

        const result = await api.createExpense({ amount: 450, category: "food" });

        expect(fetch).toHaveBeenCalledTimes(1);
        const [url, options] = fetch.mock.calls[0];
        expect(url).toContain("/expenses");
        expect(options.method).toBe("POST");
        expect(options.headers["Content-Type"]).toBe("application/json");
        expect(JSON.parse(options.body)).toEqual({ amount: 450, category: "food" });
        expect(result).toEqual(fakeExpense);
    });

    test("listExpenses passes filters as query params", async () => {
        fetch.mockResolvedValue({
            ok: true,
            json: async () => ({ total: 0, total_amount: 0, items: [] }),
        });

        await api.listExpenses({ category: "food", date_from: "2025-04-01" });

        const url = fetch.mock.calls[0][0];
        expect(url).toContain("category=food");
        expect(url).toContain("date_from=2025-04-01");
    });

    test("updateExpense sends PUT to /expenses/{id}", async () => {
        fetch.mockResolvedValue({
            ok: true,
            json: async () => ({ id: "abc", amount: 500 }),
        });

        await api.updateExpense("abc", { amount: 500 });

        const [url, options] = fetch.mock.calls[0];
        expect(url).toContain("/expenses/abc");
        expect(options.method).toBe("PUT");
        expect(JSON.parse(options.body)).toEqual({ amount: 500 });
    });

    test("deleteExpense sends DELETE to /expenses/{id}", async () => {
        fetch.mockResolvedValue({ ok: true });

        const result = await api.deleteExpense("abc");

        const [url, options] = fetch.mock.calls[0];
        expect(url).toContain("/expenses/abc");
        expect(options.method).toBe("DELETE");
        expect(result).toBe(true);
    });

    test("throws an Error with detail on non-ok response", async () => {
        fetch.mockResolvedValue({
            ok: false,
            status: 404,
            statusText: "Not Found",
            json: async () => ({ detail: "Expense not found" }),
        });

        await expect(api.deleteExpense("missing")).rejects.toThrow("Expense not found");
    });

    test("throws an Error with status code attached", async () => {
        fetch.mockResolvedValue({
            ok: false,
            status: 422,
            statusText: "Unprocessable Entity",
            json: async () => ({ detail: "Validation error" }),
        });

        try {
            await api.createExpense({ amount: -1 });
            throw new Error("Should have thrown");
        } catch (err) {
            expect(err.status).toBe(422);
            expect(err.message).toBe("Validation error");
        }
    });
});
