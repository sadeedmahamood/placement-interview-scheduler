// import { useEffect, useState } from "react";
// import "./App.css";

// function App() {
//   const [interviews, setInterviews] = useState([]);
//   const [companies, setCompanies] = useState([]);
//   const [students, setStudents] = useState([]);
//   const [panels, setPanels] = useState([]);
//   const [rooms, setRooms] = useState([]);
//   const [problems, setProblems] = useState([]);
//   const [changeSummary, setChangeSummary] = useState([]);

//   const [loading, setLoading] = useState(true);
//   const [error, setError] = useState("");
//   const [actionError, setActionError] = useState("");
//   const [replanning, setReplanning] = useState(false);

//   const [selectedCompany, setSelectedCompany] = useState("");
//   const [delayHours, setDelayHours] = useState("");
//   const [selectedPanel, setSelectedPanel] = useState("");
//   const [selectedRoom, setSelectedRoom] = useState("");
//   const [selectedStudent, setSelectedStudent] = useState("");

//   const [currentPage, setCurrentPage] = useState(1);

//   const interviewsPerPage = 25;

//   // Fetch all pages from Django
//   const fetchAllInterviews = async (url) => {
//     let allInterviews = [];
//     let page = 1;
//     let hasNextPage = true;

//     while (hasNextPage) {
//       const separator = url.includes("?") ? "&" : "?";

//       const response = await fetch(
//         `${url}${separator}page_size=100&page=${page}`
//       );

//       if (!response.ok) {
//         throw new Error("Failed to fetch interviews");
//       }

//       const data = await response.json();

//       allInterviews = [
//         ...allInterviews,
//         ...(data.results || []),
//       ];

//       hasNextPage = Boolean(data.next);
//       page += 1;
//     }

//     return allInterviews;
//   };

//   const fetchSchedule = () => {
//     return fetchAllInterviews("/api/interviews/");
//   };

//   const fetchProblems = () => {
//     return fetchAllInterviews(
//       "/api/interviews/?status=UNSCHEDULED"
//     );
//   };

//   // Load all dashboard data
//   const loadData = async () => {
//     try {
//       setLoading(true);
//       setError("");

//       const [
//         schedule,
//         unscheduled,
//         companiesResponse,
//         studentsResponse,
//         panelsResponse,
//         roomsResponse,
//       ] = await Promise.all([
//         fetchSchedule(),
//         fetchProblems(),
//         fetch("/api/companys/"),
//         fetch("/api/students/"),
//         fetch("/api/panels/"),
//         fetch("/api/rooms/"),
//       ]);

//       if (
//         !companiesResponse.ok ||
//         !studentsResponse.ok ||
//         !panelsResponse.ok ||
//         !roomsResponse.ok
//       ) {
//         throw new Error("Failed to load dashboard data");
//       }

//       const [
//         companiesData,
//         studentsData,
//         panelsData,
//         roomsData,
//       ] = await Promise.all([
//         companiesResponse.json(),
//         studentsResponse.json(),
//         panelsResponse.json(),
//         roomsResponse.json(),
//       ]);

//       setInterviews(schedule);
//       setProblems(unscheduled);
//       setCompanies(companiesData);
//       setStudents(studentsData);
//       setPanels(panelsData);
//       setRooms(roomsData);
//       setCurrentPage(1);
//     } catch (err) {
//       setError(err.message);
//     } finally {
//       setLoading(false);
//     }
//   };

//   useEffect(() => {
//     loadData();
//   }, []);

//   // Refresh only schedule-related data
//   const refreshSchedule = async () => {
//     const [schedule, unscheduled] = await Promise.all([
//       fetchSchedule(),
//       fetchProblems(),
//     ]);

//     setInterviews(schedule);
//     setProblems(unscheduled);
//     setCurrentPage(1);
//   };

//   // Send disturbance to backend
//   const performReplan = async (payload) => {
//     try {
//       setReplanning(true);
//       setActionError("");

//       const response = await fetch("/api/replan/", {
//         method: "POST",
//         headers: {
//           "Content-Type": "application/json",
//         },
//         body: JSON.stringify(payload),
//       });

//       const data = await response.json();

//       if (!response.ok) {
//         throw new Error(data.error || "Replanning failed");
//       }

//       setChangeSummary(data.changes || []);

//       await refreshSchedule();
//     } catch (err) {
//       setActionError(err.message);
//     } finally {
//       setReplanning(false);
//     }
//   };

//   const handleCompanyDelay = () => {
//     if (!selectedCompany) {
//       setActionError("Please select a company.");
//       return;
//     }

//     if (!delayHours || Number(delayHours) <= 0) {
//       setActionError("Please enter a valid delay in hours.");
//       return;
//     }

//     performReplan({
//       type: "company_delay",
//       company: selectedCompany,
//       delay_hours: Number(delayHours),
//     });
//   };

//   const handlePanelDrop = () => {
//     if (!selectedPanel) {
//       setActionError("Please select a panel.");
//       return;
//     }

//     performReplan({
//       type: "panel_dropout",
//       panel: selectedPanel,
//     });
//   };

//   const handleRoomUnavailable = () => {
//     if (!selectedRoom) {
//       setActionError("Please select a room.");
//       return;
//     }

//     performReplan({
//       type: "room_unavailable",
//       room: selectedRoom,
//     });
//   };

//   const handleStudentWithdrawal = () => {
//     if (!selectedStudent) {
//       setActionError("Please select a student.");
//       return;
//     }

//     performReplan({
//       type: "student_withdrawal",
//       student: selectedStudent,
//     });
//   };

//   const dayName = (day) => {
//     const days = {
//       1: "Monday",
//       2: "Tuesday",
//       3: "Wednesday",
//       4: "Thursday",
//       5: "Friday",
//     };

//     return days[day] || "—";
//   };

//   const formatSchedule = (schedule) => {
//     if (!schedule) {
//       return "—";
//     }

//     if (
//       schedule.day &&
//       schedule.start_time &&
//       schedule.end_time
//     ) {
//       return `${dayName(schedule.day)}, ${schedule.start_time} - ${schedule.end_time}`;
//     }

//     return schedule.status || "—";
//   };

//   const totalPages = Math.ceil(
//     interviews.length / interviewsPerPage
//   );

//   const startIndex =
//     (currentPage - 1) * interviewsPerPage;

//   const currentInterviews = interviews.slice(
//     startIndex,
//     startIndex + interviewsPerPage
//   );

//   return (
//     <div className="app">
//       <header className="header">
//         <div>
//           <h1>Placement Interview Scheduler</h1>
//           <p>Coordinator Dashboard</p>
//         </div>

//         <button
//           className="refresh-button"
//           onClick={loadData}
//           disabled={loading || replanning}
//         >
//           {loading ? "Loading..." : "Refresh"}
//         </button>
//       </header>

//       <main>
//         {error && (
//           <div className="message error">
//             {error}
//           </div>
//         )}

//         {actionError && (
//           <div className="message error">
//             <span>{actionError}</span>

//             <button onClick={() => setActionError("")}>
//               ×
//             </button>
//           </div>
//         )}

//         {/* Current Schedule */}
//         <section className="card">
//           <div className="section-heading">
//             <div>
//               <h2>Current Schedule</h2>
//               <p>
//                 Scheduled and unscheduled interview assignments.
//               </p>
//             </div>

//             <span className="count">
//               {interviews.length} interviews
//             </span>
//           </div>

//           {loading ? (
//             <div className="empty-state">
//               Loading interviews...
//             </div>
//           ) : interviews.length === 0 ? (
//             <div className="empty-state">
//               No interviews found.
//             </div>
//           ) : (
//             <>
//               <div className="table-wrapper">
//                 <table>
//                   <thead>
//                     <tr>
//                       <th>Student</th>
//                       <th>Company</th>
//                       <th>Day</th>
//                       <th>Start</th>
//                       <th>End</th>
//                       <th>Panel</th>
//                       <th>Room</th>
//                       <th>Status</th>
//                     </tr>
//                   </thead>

//                   <tbody>
//                     {currentInterviews.map((interview) => (
//                       <tr key={interview.id}>
//                         <td>{interview.student}</td>
//                         <td>{interview.company}</td>
//                         <td>{dayName(interview.day)}</td>
//                         <td>{interview.start_time || "—"}</td>
//                         <td>{interview.end_time || "—"}</td>
//                         <td>{interview.panel || "—"}</td>
//                         <td>{interview.room || "—"}</td>
//                         <td>
//                           <span
//                             className={`status ${String(
//                               interview.status
//                             ).toLowerCase()}`}
//                           >
//                             {interview.status}
//                           </span>
//                         </td>
//                       </tr>
//                     ))}
//                   </tbody>
//                 </table>
//               </div>

//               <div className="pagination">
//                 <span>
//                   Showing {startIndex + 1} -{" "}
//                   {Math.min(
//                     startIndex + interviewsPerPage,
//                     interviews.length
//                   )}{" "}
//                   of {interviews.length} interviews
//                 </span>

//                 <div className="pagination-buttons">
//                   <button
//                     onClick={() =>
//                       setCurrentPage((page) =>
//                         Math.max(page - 1, 1)
//                       )
//                     }
//                     disabled={currentPage === 1}
//                   >
//                     ← Previous
//                   </button>

//                   <span className="page-number">
//                     Page {currentPage} of {totalPages}
//                   </span>

//                   <button
//                     onClick={() =>
//                       setCurrentPage((page) =>
//                         Math.min(page + 1, totalPages)
//                       )
//                     }
//                     disabled={currentPage === totalPages}
//                   >
//                     Next →
//                   </button>
//                 </div>
//               </div>
//             </>
//           )}
//         </section>

//         {/* Problems */}
//         <section className="card">
//           <div className="section-heading">
//             <div>
//               <h2>Problems / Conflicts</h2>
//               <p>
//                 Interviews currently marked as unscheduled.
//               </p>
//             </div>

//             <span className="count">
//               {problems.length} problems
//             </span>
//           </div>

//           {problems.length === 0 ? (
//             <div className="success-state">
//               No unscheduled interviews.
//             </div>
//           ) : (
//             <div className="table-wrapper">
//               <table>
//                 <thead>
//                   <tr>
//                     <th>Student</th>
//                     <th>Company</th>
//                     <th>Day</th>
//                     <th>Start</th>
//                     <th>End</th>
//                     <th>Panel</th>
//                     <th>Room</th>
//                     <th>Status</th>
//                   </tr>
//                 </thead>

//                 <tbody>
//                   {problems.map((interview) => (
//                     <tr key={interview.id}>
//                       <td>{interview.student}</td>
//                       <td>{interview.company}</td>
//                       <td>{dayName(interview.day)}</td>
//                       <td>{interview.start_time || "—"}</td>
//                       <td>{interview.end_time || "—"}</td>
//                       <td>{interview.panel || "—"}</td>
//                       <td>{interview.room || "—"}</td>
//                       <td>
//                         <span className="status unscheduled">
//                           {interview.status}
//                         </span>
//                       </td>
//                     </tr>
//                   ))}
//                 </tbody>
//               </table>
//             </div>
//           )}
//         </section>

//         {/* Actions */}
//         <section className="card">
//           <div className="section-heading">
//             <div>
//               <h2>Problems / Actions</h2>
//               <p>
//                 Apply disturbances and trigger automatic
//                 replanning.
//               </p>
//             </div>
//           </div>

//           <div className="actions-grid">
//             {/* Company Delay */}
//             <div className="action-box">
//               <h3>Company Delay</h3>
//               <p>
//                 Delay all affected interviews for a company.
//               </p>

//               <select
//                 value={selectedCompany}
//                 onChange={(event) =>
//                   setSelectedCompany(event.target.value)
//                 }
//               >
//                 <option value="">Select Company</option>

//                 {companies.map((company) => (
//                   <option
//                     key={company.company_id}
//                     value={company.company_id}
//                   >
//                     {company.company_id} - {company.name}
//                   </option>
//                 ))}
//               </select>

//               <input
//                 type="number"
//                 min="1"
//                 step="1"
//                 placeholder="Delay hours"
//                 value={delayHours}
//                 onChange={(event) =>
//                   setDelayHours(event.target.value)
//                 }
//               />

//               <button
//                 onClick={handleCompanyDelay}
//                 disabled={replanning}
//               >
//                 {replanning ? "Replanning..." : "Replan"}
//               </button>
//             </div>

//             {/* Panel Drop */}
//             <div className="action-box">
//               <h3>Panel Drop</h3>
//               <p>
//                 Mark a panel unavailable and replan affected
//                 interviews.
//               </p>

//               <select
//                 value={selectedPanel}
//                 onChange={(event) =>
//                   setSelectedPanel(event.target.value)
//                 }
//               >
//                 <option value="">Select Panel</option>

//                 {panels.map((panel) => (
//                   <option
//                     key={panel.panel_id}
//                     value={panel.panel_id}
//                   >
//                     {panel.panel_id} - {panel.name}
//                   </option>
//                 ))}
//               </select>

//               <button
//                 onClick={handlePanelDrop}
//                 disabled={replanning}
//               >
//                 {replanning ? "Replanning..." : "Replan"}
//               </button>
//             </div>

//             {/* Room Unavailable */}
//             <div className="action-box">
//               <h3>Room Unavailable</h3>
//               <p>
//                 Make a room unavailable and replan its
//                 interviews.
//               </p>

//               <select
//                 value={selectedRoom}
//                 onChange={(event) =>
//                   setSelectedRoom(event.target.value)
//                 }
//               >
//                 <option value="">Select Room</option>

//                 {rooms.map((room) => (
//                   <option
//                     key={room.room_id}
//                     value={room.room_id}
//                   >
//                     {room.room_id} - {room.name}
//                   </option>
//                 ))}
//               </select>

//               <button
//                 onClick={handleRoomUnavailable}
//                 disabled={replanning}
//               >
//                 {replanning ? "Replanning..." : "Replan"}
//               </button>
//             </div>

//             {/* Student Withdrawal */}
//             <div className="action-box">
//               <h3>Student Withdrawal</h3>
//               <p>
//                 Withdraw a student and update the schedule.
//               </p>

//               <select
//                 value={selectedStudent}
//                 onChange={(event) =>
//                   setSelectedStudent(event.target.value)
//                 }
//               >
//                 <option value="">Select Student</option>

//                 {students.map((student) => (
//                   <option
//                     key={student.student_id}
//                     value={student.student_id}
//                   >
//                     {student.student_id} - {student.name}
//                   </option>
//                 ))}
//               </select>

//               <button
//                 onClick={handleStudentWithdrawal}
//                 disabled={replanning}
//               >
//                 {replanning ? "Processing..." : "Withdraw"}
//               </button>
//             </div>
//           </div>
//         </section>

//         {/* Change Summary */}
//         <section className="card">
//           <div className="section-heading">
//             <div>
//               <h2>Change Summary</h2>
//               <p>
//                 Changes returned by the replanning engine.
//               </p>
//             </div>

//             <span className="count">
//               {changeSummary.length} changes
//             </span>
//           </div>

//           {changeSummary.length === 0 ? (
//             <div className="empty-state">
//               No replanning changes yet.
//             </div>
//           ) : (
//             <div className="table-wrapper">
//               <table>
//                 <thead>
//                   <tr>
//                     <th>Student</th>
//                     <th>Company</th>
//                     <th>Old Room</th>
//                     <th>New Room</th>
//                     <th>Old Panel</th>
//                     <th>New Panel</th>
//                     <th>Old Schedule</th>
//                     <th>New Schedule</th>
//                     <th>Status</th>
//                     <th>Inform</th>
//                   </tr>
//                 </thead>

//                 <tbody>
//                   {changeSummary.map((change, index) => (
//                     <tr key={`${change.student}-${change.company}-${index}`}>
//                       <td>{change.student}</td>
//                       <td>{change.company}</td>

//                       <td>{change.old?.room || "—"}</td>
//                       <td>{change.new?.room || "—"}</td>

//                       <td>{change.old?.panel || "—"}</td>
//                       <td>{change.new?.panel || "—"}</td>

//                       <td>
//                         {formatSchedule(change.old)}
//                       </td>

//                       <td>
//                         {formatSchedule(change.new)}
//                       </td>

//                       <td>
//                         <span
//                           className={`status ${String(
//                             change.status || ""
//                           ).toLowerCase().replaceAll(" ", "-")}`}
//                         >
//                           {change.status || "—"}
//                         </span>
//                       </td>

//                       <td>
//                         {change.inform?.length
//                           ? change.inform.join(", ")
//                           : "—"}
//                       </td>
//                     </tr>
//                   ))}
//                 </tbody>
//               </table>
//             </div>
//           )}
//         </section>
//       </main>
//     </div>
//   );
// }

// export default App;




import { useEffect, useState } from "react";
import "./App.css";

function App() {
  const [interviews, setInterviews] = useState([]);
  const [companies, setCompanies] = useState([]);
  const [students, setStudents] = useState([]);
  const [panels, setPanels] = useState([]);
  const [rooms, setRooms] = useState([]);
  const [problems, setProblems] = useState([]);
  const [changeSummary, setChangeSummary] = useState([]);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [actionError, setActionError] = useState("");
  const [replanning, setReplanning] = useState(false);

  const [selectedCompany, setSelectedCompany] = useState("");
  const [delayHours, setDelayHours] = useState("");
  const [selectedPanel, setSelectedPanel] = useState("");
  const [selectedRoom, setSelectedRoom] = useState("");
  const [selectedStudent, setSelectedStudent] = useState("");

  const [currentPage, setCurrentPage] = useState(1);

  const interviewsPerPage = 25;

  const fetchAllInterviews = async (url) => {
    let allInterviews = [];
    let page = 1;
    let hasNextPage = true;

    while (hasNextPage) {
      const separator = url.includes("?") ? "&" : "?";

      const response = await fetch(
        `${url}${separator}page_size=100&page=${page}`
      );

      if (!response.ok) {
        throw new Error("Failed to fetch interviews");
      }

      const data = await response.json();

      allInterviews = [
        ...allInterviews,
        ...(data.results || []),
      ];

      hasNextPage = Boolean(data.next);
      page += 1;
    }

    return allInterviews;
  };

  const fetchSchedule = () => {
    return fetchAllInterviews("/api/interviews/");
  };

  const fetchProblems = () => {
    return fetchAllInterviews(
      "/api/interviews/?status=UNSCHEDULED"
    );
  };

  const loadData = async () => {
    try {
      setLoading(true);
      setError("");

      const [
        schedule,
        unscheduled,
        companiesResponse,
        studentsResponse,
        panelsResponse,
        roomsResponse,
      ] = await Promise.all([
        fetchSchedule(),
        fetchProblems(),
        fetch("/api/companys/"),
        fetch("/api/students/"),
        fetch("/api/panels/"),
        fetch("/api/rooms/"),
      ]);

      if (
        !companiesResponse.ok ||
        !studentsResponse.ok ||
        !panelsResponse.ok ||
        !roomsResponse.ok
      ) {
        throw new Error("Failed to load dashboard data");
      }

      const [
        companiesData,
        studentsData,
        panelsData,
        roomsData,
      ] = await Promise.all([
        companiesResponse.json(),
        studentsResponse.json(),
        panelsResponse.json(),
        roomsResponse.json(),
      ]);

      setInterviews(schedule);
      setProblems(unscheduled);
      setCompanies(companiesData);
      setStudents(studentsData);
      setPanels(panelsData);
      setRooms(roomsData);
      setCurrentPage(1);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const refreshSchedule = async () => {
    const [schedule, unscheduled] = await Promise.all([
      fetchSchedule(),
      fetchProblems(),
    ]);

    setInterviews(schedule);
    setProblems(unscheduled);
    setCurrentPage(1);
  };

  const performReplan = async (payload) => {
    try {
      setReplanning(true);
      setActionError("");

      const response = await fetch("/api/replan/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Replanning failed");
      }

      setChangeSummary(data.changes || []);

      await refreshSchedule();
    } catch (err) {
      setActionError(err.message);
    } finally {
      setReplanning(false);
    }
  };

  const handleCompanyDelay = () => {
    if (!selectedCompany) {
      setActionError("Please select a company.");
      return;
    }

    if (!delayHours || Number(delayHours) <= 0) {
      setActionError("Please enter a valid delay in hours.");
      return;
    }

    performReplan({
      type: "company_delay",
      company: selectedCompany,
      delay_hours: Number(delayHours),
    });
  };

  const handlePanelDrop = () => {
    if (!selectedPanel) {
      setActionError("Please select a panel.");
      return;
    }

    performReplan({
      type: "panel_dropout",
      panel: selectedPanel,
    });
  };

  const handleRoomUnavailable = () => {
    if (!selectedRoom) {
      setActionError("Please select a room.");
      return;
    }

    performReplan({
      type: "room_unavailable",
      room: selectedRoom,
    });
  };

  const handleStudentWithdrawal = () => {
    if (!selectedStudent) {
      setActionError("Please select a student.");
      return;
    }

    performReplan({
      type: "student_withdrawal",
      student: selectedStudent,
    });
  };

  const dayName = (day) => {
    const days = {
      1: "Monday",
      2: "Tuesday",
      3: "Wednesday",
      4: "Thursday",
      5: "Friday",
    };

    return days[day] || "—";
  };

  // FIXED:
  // If there is no actual schedule, show "—".
  // Never show status inside the schedule column.
  const formatSchedule = (schedule) => {
    if (
      schedule?.day &&
      schedule?.start_time &&
      schedule?.end_time
    ) {
      return `${dayName(schedule.day)}, ${schedule.start_time} - ${schedule.end_time}`;
    }

    return "—";
  };

  const totalPages = Math.ceil(
    interviews.length / interviewsPerPage
  );

  const startIndex =
    (currentPage - 1) * interviewsPerPage;

  const currentInterviews = interviews.slice(
    startIndex,
    startIndex + interviewsPerPage
  );

  return (
    <div className="app">
      <header className="header">
        <div>
          <h1>Placement Interview Scheduler</h1>
          <p>Coordinator Dashboard</p>
        </div>

        <button
          className="refresh-button"
          onClick={async () => {
            // Clear old action result when manually refreshing.
            setChangeSummary([]);
            setActionError("");
            await loadData();
          }}
          disabled={loading || replanning}
        >
          {loading ? "Loading..." : "Refresh"}
        </button>
      </header>

      <main>
        {error && (
          <div className="message error">
            {error}
          </div>
        )}

        {actionError && (
          <div className="message error">
            <span>{actionError}</span>

            <button onClick={() => setActionError("")}>
              ×
            </button>
          </div>
        )}

        {/* CURRENT SCHEDULE */}
        <section className="card">
          <div className="section-heading">
            <div>
              <h2>Current Schedule</h2>
              <p>
                Scheduled and unscheduled interview assignments.
              </p>
            </div>

            <span className="count">
              {interviews.length} interviews
            </span>
          </div>

          {loading ? (
            <div className="empty-state">
              Loading interviews...
            </div>
          ) : interviews.length === 0 ? (
            <div className="empty-state">
              No interviews found.
            </div>
          ) : (
            <>
              <div className="table-wrapper">
                <table>
                  <thead>
                    <tr>
                      <th>Student</th>
                      <th>Company</th>
                      <th>Day</th>
                      <th>Start</th>
                      <th>End</th>
                      <th>Panel</th>
                      <th>Room</th>
                      <th>Status</th>
                    </tr>
                  </thead>

                  <tbody>
                    {currentInterviews.map((interview) => (
                      <tr key={interview.id}>
                        <td>{interview.student}</td>
                        <td>{interview.company}</td>
                        <td>{dayName(interview.day)}</td>
                        <td>{interview.start_time || "—"}</td>
                        <td>{interview.end_time || "—"}</td>
                        <td>{interview.panel || "—"}</td>
                        <td>{interview.room || "—"}</td>
                        <td>
                          <span
                            className={`status ${String(
                              interview.status
                            ).toLowerCase()}`}
                          >
                            {interview.status}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              <div className="pagination">
                <span>
                  Showing {startIndex + 1} -{" "}
                  {Math.min(
                    startIndex + interviewsPerPage,
                    interviews.length
                  )}{" "}
                  of {interviews.length} interviews
                </span>

                <div className="pagination-buttons">
                  <button
                    onClick={() =>
                      setCurrentPage((page) =>
                        Math.max(page - 1, 1)
                      )
                    }
                    disabled={currentPage === 1}
                  >
                    ← Previous
                  </button>

                  <span className="page-number">
                    Page {currentPage} of {totalPages}
                  </span>

                  <button
                    onClick={() =>
                      setCurrentPage((page) =>
                        Math.min(page + 1, totalPages)
                      )
                    }
                    disabled={currentPage === totalPages}
                  >
                    Next →
                  </button>
                </div>
              </div>
            </>
          )}
        </section>

        {/* PROBLEMS */}
        <section className="card">
          <div className="section-heading">
            <div>
              <h2>Problems / Conflicts</h2>
              <p>
                Interviews currently marked as unscheduled.
              </p>
            </div>

            <span className="count">
              {problems.length} problems
            </span>
          </div>

          {problems.length === 0 ? (
            <div className="success-state">
              No unscheduled interviews.
            </div>
          ) : (
            <div className="table-wrapper">
              <table>
                <thead>
                  <tr>
                    <th>Student</th>
                    <th>Company</th>
                    <th>Day</th>
                    <th>Start</th>
                    <th>End</th>
                    <th>Panel</th>
                    <th>Room</th>
                    <th>Status</th>
                  </tr>
                </thead>

                <tbody>
                  {problems.map((interview) => (
                    <tr key={interview.id}>
                      <td>{interview.student}</td>
                      <td>{interview.company}</td>
                      <td>{dayName(interview.day)}</td>
                      <td>{interview.start_time || "—"}</td>
                      <td>{interview.end_time || "—"}</td>
                      <td>{interview.panel || "—"}</td>
                      <td>{interview.room || "—"}</td>
                      <td>
                        <span className="status unscheduled">
                          {interview.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>

        {/* ACTIONS */}
        <section className="card">
          <div className="section-heading">
            <div>
              <h2>Problems / Actions</h2>
              <p>
                Apply disturbances and trigger automatic
                replanning.
              </p>
            </div>
          </div>

          <div className="actions-grid">

            {/* COMPANY DELAY */}
            <div className="action-box">
              <h3>Company Delay</h3>
              <p>
                Delay all affected interviews for a company.
              </p>

              <select
                value={selectedCompany}
                onChange={(event) =>
                  setSelectedCompany(event.target.value)
                }
              >
                <option value="">Select Company</option>

                {companies.map((company) => (
                  <option
                    key={company.company_id}
                    value={company.company_id}
                  >
                    {company.company_id} - {company.name}
                  </option>
                ))}
              </select>

              <input
                type="number"
                min="1"
                step="1"
                placeholder="Delay hours"
                value={delayHours}
                onChange={(event) =>
                  setDelayHours(event.target.value)
                }
              />

              <button
                onClick={handleCompanyDelay}
                disabled={replanning}
              >
                {replanning ? "Replanning..." : "Replan"}
              </button>
            </div>

            {/* PANEL DROP */}
            <div className="action-box">
              <h3>Panel Drop</h3>
              <p>
                Mark a panel unavailable and replan affected
                interviews.
              </p>

              <select
                value={selectedPanel}
                onChange={(event) =>
                  setSelectedPanel(event.target.value)
                }
              >
                <option value="">Select Panel</option>

                {panels.map((panel) => (
                  <option
                    key={panel.panel_id}
                    value={panel.panel_id}
                  >
                    {panel.panel_id} - {panel.name}
                  </option>
                ))}
              </select>

              <button
                onClick={handlePanelDrop}
                disabled={replanning}
              >
                {replanning ? "Replanning..." : "Replan"}
              </button>
            </div>

            {/* ROOM UNAVAILABLE */}
            <div className="action-box">
              <h3>Room Unavailable</h3>
              <p>
                Make a room unavailable and replan its
                interviews.
              </p>

              <select
                value={selectedRoom}
                onChange={(event) =>
                  setSelectedRoom(event.target.value)
                }
              >
                <option value="">Select Room</option>

                {rooms.map((room) => (
                  <option
                    key={room.room_id}
                    value={room.room_id}
                  >
                    {room.room_id} - {room.name}
                  </option>
                ))}
              </select>

              <button
                onClick={handleRoomUnavailable}
                disabled={replanning}
              >
                {replanning ? "Replanning..." : "Replan"}
              </button>
            </div>

            {/* STUDENT WITHDRAWAL */}
            <div className="action-box">
              <h3>Student Withdrawal</h3>
              <p>
                Withdraw a student and update the schedule.
              </p>

              <select
                value={selectedStudent}
                onChange={(event) =>
                  setSelectedStudent(event.target.value)
                }
              >
                <option value="">Select Student</option>

                {students.map((student) => (
                  <option
                    key={student.student_id}
                    value={student.student_id}
                  >
                    {student.student_id} - {student.name}
                  </option>
                ))}
              </select>

              <button
                onClick={handleStudentWithdrawal}
                disabled={replanning}
              >
                {replanning ? "Processing..." : "Withdraw"}
              </button>
            </div>
          </div>
        </section>

        {/* CHANGE SUMMARY */}
        <section className="card">
          <div className="section-heading">
            <div>
              <h2>Change Summary</h2>
              <p>
                Changes returned by the replanning engine.
              </p>
            </div>

            <span className="count">
              {changeSummary.length} changes
            </span>
          </div>

          {changeSummary.length === 0 ? (
            <div className="empty-state">
              No replanning changes yet.
            </div>
          ) : (
            <div className="table-wrapper">
              <table>
                <thead>
                  <tr>
                    <th>Student</th>
                    <th>Company</th>
                    <th>Old Room</th>
                    <th>New Room</th>
                    <th>Old Panel</th>
                    <th>New Panel</th>
                    <th>Old Schedule</th>
                    <th>New Schedule</th>
                    <th>Status</th>
                    <th>Inform</th>
                  </tr>
                </thead>

                <tbody>
                  {changeSummary.map((change, index) => (
                    <tr
                      key={`${change.student}-${change.company}-${index}`}
                    >
                      <td>{change.student}</td>
                      <td>{change.company}</td>

                      <td>
                        {change.old?.room || "—"}
                      </td>

                      <td>
                        {change.new?.room || "—"}
                      </td>

                      <td>
                        {change.old?.panel || "—"}
                      </td>

                      <td>
                        {change.new?.panel || "—"}
                      </td>

                      <td>
                        {formatSchedule(change.old)}
                      </td>

                      <td>
                        {formatSchedule(change.new)}
                      </td>

                      <td>
                        <span
                          className={`status ${String(
                            change.status || ""
                          )
                            .toLowerCase()
                            .replaceAll(" ", "-")}`}
                        >
                          {change.status || "—"}
                        </span>
                      </td>

                      <td>
                        {change.inform?.length
                          ? change.inform.join(", ")
                          : "—"}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>
      </main>
    </div>
  );
}

export default App;