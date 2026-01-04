// --- DASHBOARD LOGIC ---
async function loadTeamDashboard() {
    const container = document.getElementById('team-reports-container');
    container.innerHTML = '<div class="p-6 text-center text-gray-500">Loading data...</div>';
    try {
        const res = await authenticatedFetch('/TeamData/');
        if (!res.ok) throw new Error("Access Denied");
        
        const data = await res.json();
        
        // Update stats
        document.getElementById('total-teams-count').innerText = data.length;
        let totalIssues = 0;
        
        container.innerHTML = '';
        
        if (data.length === 0) {
            container.innerHTML = '<div class="p-6 text-center text-gray-500">No team data generated yet.</div>';
            return;
        }
        data.forEach(team => {
            const issueCount = team.common_problems ? team.common_problems.length : 0;
            totalIssues += issueCount;
            
            const el = document.createElement('div');
            el.className = "p-6 hover:bg-gray-50";
            el.innerHTML = `
                <div class="flex justify-between items-start">
                    <div>
                        <h4 class="text-lg font-bold text-indigo-700">Team Report #${team.id || 'N/A'}</h4>
                        <p class="mt-2 text-sm text-gray-600"><strong>Summary:</strong> ${team.summary.substring(0, 100)}...</p>
                    </div>
                    <span class="bg-red-100 text-red-800 text-xs font-semibold mr-2 px-2.5 py-0.5 rounded">
                        ${issueCount} Issues
                    </span>
                </div>
                <div class="mt-4">
                    <h5 class="text-xs font-bold text-gray-500 uppercase">Recommendation:</h5>
                    <p class="text-sm text-gray-700 italic border-l-2 border-green-500 pl-2 mt-1">
                        ${team.recommendation}
                    </p>
                </div>
            `;
            container.appendChild(el);
        });
        document.getElementById('common-issues-count').innerText = totalIssues;
    } catch (err) {
        container.innerHTML = '<div class="p-6 text-center text-red-500">You do not have permission to view team data.</div>';
    }
}