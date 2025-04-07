/**
 * Create a force-directed graph visualization using D3.js
 * @param {Object} data - The visualization data
 * @param {string} elementId - The ID of the HTML element to contain the visualization
 */
function createForceGraph(data, elementId) {
    // Clear previous visualization
    d3.select(`#${elementId}`).html('');

    // Set up SVG dimensions
    const width = 800;
    const height = 600;

    // Create SVG element
    const svg = d3.select(`#${elementId}`)
        .append('svg')
        .attr('width', width)
        .attr('height', height)
        .attr('viewBox', `0 0 ${width} ${height}`)
        .attr('class', 'border rounded');

    // Create a group for the graph
    const g = svg.append('g');

    // Add zoom functionality
    const zoom = d3.zoom()
        .scaleExtent([0.1, 4])
        .on('zoom', (event) => {
            g.attr('transform', event.transform);
        });

    svg.call(zoom);

    // Create a color scale for clusters
    const colorScale = d3.scaleOrdinal(d3.schemeCategory10);

    // Create the simulation
    const simulation = d3.forceSimulation(data.nodes)
        .force('link', d3.forceLink(data.links).id(d => d.id).distance(100))
        .force('charge', d3.forceManyBody().strength(-200))
        .force('center', d3.forceCenter(width / 2, height / 2))
        .force('collision', d3.forceCollide().radius(30));

    // Create links
    const link = g.append('g')
        .attr('class', 'links')
        .selectAll('line')
        .data(data.links)
        .enter()
        .append('line')
        .attr('stroke-width', d => d.type === 'pmid_to_dataset' ? 2 : 1)
        .attr('stroke', d => d.type === 'pmid_to_dataset' ? '#999' : '#ddd')
        .attr('stroke-opacity', d => d.type === 'pmid_to_dataset' ? 0.8 : 0.4);

    // Create nodes
    const node = g.append('g')
        .attr('class', 'nodes')
        .selectAll('g')
        .data(data.nodes)
        .enter()
        .append('g')
        .call(d3.drag()
            .on('start', dragstarted)
            .on('drag', dragged)
            .on('end', dragended));

    // Add circles to nodes
    node.append('circle')
        .attr('r', d => d.type === 'pmid' ? 15 : 10)
        .attr('fill', d => d.type === 'pmid' ? '#f9a03c' : colorScale(d.cluster))
        .attr('stroke', '#fff')
        .attr('stroke-width', 1.5);

    // Add labels to nodes
    node.append('text')
        .attr('dx', 12)
        .attr('dy', 4)
        .text(d => d.type === 'pmid' ? `PMID: ${d.id}` : d.id)
        .attr('font-size', '10px');

    // Add title for tooltips
    node.append('title')
        .text(d => {
            if (d.type === 'pmid') {
                return `PMID: ${d.id}`;
            } else {
                return `${d.id}\n${d.title}\nType: ${d.experiment_type}\nOrganism: ${d.organism}\nPMID: ${d.pmid}`;
            }
        });

    // Update positions on each tick
    simulation.on('tick', () => {
        link
            .attr('x1', d => d.source.x)
            .attr('y1', d => d.source.y)
            .attr('x2', d => d.target.x)
            .attr('y2', d => d.target.y);

        node
            .attr('transform', d => `translate(${d.x},${d.y})`);
    });

    // Drag functions
    function dragstarted(event, d) {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
    }

    function dragged(event, d) {
        d.fx = event.x;
        d.fy = event.y;
    }

    function dragended(event, d) {
        if (!event.active) simulation.alphaTarget(0);
        d.fx = null;
        d.fy = null;
    }

    // Add legend
    const legend = svg.append('g')
        .attr('class', 'legend')
        .attr('transform', 'translate(20, 20)');

    // Dataset node legend item
    const datasetLegend = legend.append('g');
    datasetLegend.append('circle')
        .attr('r', 6)
        .attr('fill', colorScale(0))
        .attr('stroke', '#fff')
        .attr('stroke-width', 1.5);
    datasetLegend.append('text')
        .attr('x', 15)
        .attr('y', 4)
        .text('Dataset')
        .attr('font-size', '12px');

    // PMID node legend item
    const pmidLegend = legend.append('g')
        .attr('transform', 'translate(0, 25)');
    pmidLegend.append('circle')
        .attr('r', 6)
        .attr('fill', '#f9a03c')
        .attr('stroke', '#fff')
        .attr('stroke-width', 1.5);
    pmidLegend.append('text')
        .attr('x', 15)
        .attr('y', 4)
        .text('PMID')
        .attr('font-size', '12px');

    return {
        svg,
        simulation
    };
}