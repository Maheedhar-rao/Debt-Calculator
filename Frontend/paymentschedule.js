import React, { useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import axios from "axios";

const PaymentSchedule = () => {
  const [debt, setDebt] = useState("");
  const [startDate, setStartDate] = useState("");
  const [weeks, setWeeks] = useState("");
  const [schedule, setSchedule] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    setError("");
    setLoading(true);
    if (!debt || !startDate || !weeks) {
      setError("Please fill in all fields.");
      setLoading(false);
      return;
    }

    try {
      const response = await axios.post("https://debt-calculator-g56j.onrender.com", {
        debt: parseFloat(debt),
        start_date: startDate,
        weeks: parseInt(weeks, 10),
      });
      setSchedule(response.data.payments);
    } catch (err) {
      setError(err.response?.data?.detail || "Error fetching schedule.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-lg mx-auto p-6 bg-white shadow-md rounded-lg dark:bg-gray-800">
      <h2 className="text-xl font-bold mb-4 text-gray-900 dark:text-white">Payment Schedule Calculator</h2>
      <Input type="number" placeholder="Debt Amount" value={debt} onChange={(e) => setDebt(e.target.value)} />
      <Input type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} className="mt-2" />
      <Input type="number" placeholder="Number of Weeks" value={weeks} onChange={(e) => setWeeks(e.target.value)} className="mt-2" />
      <Button onClick={handleSubmit} className="mt-4 w-full" disabled={loading}>{loading ? "Calculating..." : "Calculate"}</Button>
      {error && <p className="text-red-500 mt-2">{error}</p>}
      {schedule && (
        <Card className="mt-6">
          <CardContent>
            <h3 className="font-semibold text-gray-900 dark:text-white">Payment Schedule</h3>
            <ul className="mt-2">
              {schedule.map((payment, index) => (
                <li key={index} className="border-b py-2 text-gray-700 dark:text-gray-300">
                  {payment.date} ({payment.day}): <strong>${payment.amount.toFixed(2)}</strong>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default PaymentSchedule;
