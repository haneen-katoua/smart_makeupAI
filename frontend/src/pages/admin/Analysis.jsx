import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import api from "../../services/api";
import "../../styles/Analysis.css";


function Analysis() {

    const [analyses, setAnalyses] = useState([]);

    const [occasion, setOccasion] = useState("");

    const [date, setDate] = useState("");

    const [search, setSearch] = useState("");

    const navigate = useNavigate();


    useEffect(() => {

        fetchAnalyses();

    }, []);


    const fetchAnalyses = async () => {

        try {

            const params = {};


            if (occasion !== "") {
                params.occasion = occasion;
            }


            if (date !== "") {
                params.date = date;
            }


            if (search !== "") {
                params.search = search;
            }


            console.log(
                "FILTER PARAMS:",
                params
            );


            const response = await api.get(
                "/api/analysis/admin/analyses/",
                {
                    params: params
                }
            );


            console.log(
                "FILTER RESULT:",
                response.data
            );


            setAnalyses(
                response.data
            );


        } catch (error) {

            console.log(
                "FILTER ERROR:",
                error.response
            );

        }

    };


    // ==========================================
    // DELETE ANALYSIS
    // ==========================================

    const handleDelete = async (id) => {

        const confirmed = window.confirm(
            "Are you sure you want to delete this analysis?"
        );


        if (!confirmed) {
            return;
        }


        try {

            await api.delete(
                `/api/analysis/admin/analyses/${id}/delete/`
            );


            // Remove the deleted analysis
            // from the current table
            setAnalyses((prevAnalyses) =>
                prevAnalyses.filter(
                    (analysis) =>
                        analysis.id !== id
                )
            );


            alert(
                "Analysis deleted successfully."
            );


        } catch (error) {

            console.error(
                "DELETE ANALYSIS ERROR:",
                error
            );


            alert(
                error.response?.data?.message ||
                "Failed to delete analysis."
            );

        }

    };


    return (

        <div className="analysis-page">


            <h1>
                Makeup Analyses
            </h1>


            {/* =========================
                FILTERS
            ========================= */}

            <div className="filters">


                <input

                    type="text"

                    placeholder="Search username"

                    value={search}

                    onChange={(e) =>
                        setSearch(
                            e.target.value
                        )
                    }

                />


                <select

                    value={occasion}

                    onChange={(e) =>
                        setOccasion(
                            e.target.value
                        )
                    }

                >

                    <option value="">
                        All Occasions
                    </option>


                    <option value="wedding">
                        Wedding
                    </option>


                    <option value="party">
                        Party
                    </option>


                    <option value="work">
                        Work
                    </option>


                    <option value="photo">
                        Photo
                    </option>


                </select>


                <input

                    type="date"

                    value={date}

                    onChange={(e) =>
                        setDate(
                            e.target.value
                        )
                    }

                />


                <button
                    className="filter-btn"
                    onClick={fetchAnalyses}
                >
                    Filter
                </button>


            </div>


            {/* =========================
                ANALYSIS TABLE
            ========================= */}

            <table className="analysis-table">


                <thead>

                    <tr>

                        <th>
                            User
                        </th>


                        <th>
                            Occasion
                        </th>


                        <th>
                            Date
                        </th>


                        <th>
                            Action
                        </th>

                    </tr>

                </thead>


                <tbody>


                    {
                        analyses.length === 0

                        ?

                        (
                            <tr>

                                <td colSpan="4">

                                    No analyses found

                                </td>

                            </tr>
                        )

                        :

                        analyses.map(
                            (analysis) => (

                                <tr
                                    key={
                                        analysis.id
                                    }
                                >


                                    <td>

                                        {
                                            analysis.username
                                        }

                                    </td>


                                    <td>

                                        {
                                            analysis.occasion
                                        }

                                    </td>


                                    <td>

                                        {
                                            new Date(
                                                analysis.created_at
                                            ).toLocaleDateString()
                                        }

                                    </td>


                                    <td>

                                        <div className="analysis-actions">


                                            {/* View Details */}

                                            <button

                                                className="view-details-btn"

                                                onClick={() =>
                                                    navigate(
                                                        `/admin/analysis/${analysis.id}`
                                                    )
                                                }

                                            >

                                                View Details

                                            </button>


                                            {/* Delete */}

                                            <button

                                                className="delete-analysis-btn"

                                                onClick={() =>
                                                    handleDelete(
                                                        analysis.id
                                                    )
                                                }

                                            >

                                                Delete

                                            </button>


                                        </div>

                                    </td>


                                </tr>

                            )
                        )
                    }


                </tbody>


            </table>


        </div>

    );

}


export default Analysis;