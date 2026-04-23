function formatTimeWithMilliseconds(timeString) {
    // 拆分日期和时间部分
    const [datePart, timePart] = timeString.split(' ');

    // 拆分时间部分
    const [hms, fractions] = timePart.split('.');

    // 提取前3位毫秒（如果不足3位则补0）
    const milliseconds = fractions ? fractions.substring(0, 3).padEnd(3, '0') : '000';

    // 组合成新格式
    return `${datePart} ${hms}.${milliseconds}`;
}

function unionName(data) {
    return [...new Set(data)]
}


function generateGrant(taskList) {
    let ganttCode = `gantt \n`;
    ganttCode += `dateFormat  YYYY-MM-DD HH:mm:ss.SSS \n`;
    // 添加节(Section)
    // ganttCode += `    section 项目阶段\n`;
    // 添加任务
    taskList.forEach(task => {
        if (task.sectionName) {
            ganttCode += `section ${task.sectionName}\n`;
        }
        if (task.data) {
            task.data.forEach(_task => {
                ganttCode += `    ${_task.name} :${_task.id}, ${_task.start}, ${_task.end}\n`;
                ganttCode += `    click ${_task.id} call renderGanttClick(${_task.id})\n`;
                ganttCode += '\n';
            })
        }

    });
    return ganttCode;
}


function bumpMillisecond(timeStr) {
    // Add 1ms to a formatted time string "YYYY-MM-DD HH:mm:ss.SSS"
    var parts = timeStr.split('.');
    var ms = parseInt(parts[1], 10) + 1;
    return parts[0] + '.' + String(ms).padStart(3, '0');
}


function renderGantt(nodesDatas, containerId) {

    const callerArray = nodesDatas.filter(_data => _data.create_time).map(({caller}) => caller);
    const unionNamecallerArray = unionName(callerArray);

    const transformData = nodesDatas
        .filter(_data => _data.create_time)
        .map(_data => {
            const endTime = _data.update_time || _data.create_time;
            const startFormatted = formatTimeWithMilliseconds(_data.create_time);
            let endFormatted = formatTimeWithMilliseconds(endTime);
            if (endFormatted === startFormatted) {
                endFormatted = bumpMillisecond(endFormatted);
            }
            return {
                ..._data,
                id: _data.node_id,
                next: _data.child_node_ids.filter(i => i),
                name: _data.callee,
                start: startFormatted,
                end: endFormatted,
            }
        })

    const transformDataSection = unionNamecallerArray.map((_caller) => {
        return {
            sectionName: _caller,
            data: transformData.filter(i => i.caller === _caller),
        }
    })

    const code = generateGrant(transformDataSection);
    $('#flowchart-container-gantt').html('').removeAttr('data-processed');
    const container = document.getElementById(containerId);
    if (transformData.length === 0) {
        container.innerHTML = '<p style="text-align:center;color:#999;padding:20px;">No completed nodes to display</p>';
        return;
    }
    container.innerHTML = code;
    mermaid.run({
        querySelector: `#${containerId}`
    });
}








