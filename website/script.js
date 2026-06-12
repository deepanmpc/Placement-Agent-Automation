document.addEventListener('DOMContentLoaded', () => {
    
    // Copy clone command
    const cloneBtn = document.getElementById('clone-btn');
    cloneBtn.addEventListener('click', () => {
        navigator.clipboard.writeText('git clone https://github.com/deepanmpc/COWORK_AGENT_DESKTOP_AUTOMATION');
        cloneBtn.classList.add('copied');
        setTimeout(() => {
            cloneBtn.classList.remove('copied');
        }, 2000);
    });

    // Typewriter effect for the hero terminal
    const textToType = "Open Google Docs and write a 500-word essay about Paris...";
    const typewriterElement = document.getElementById('typewriter');
    const agentCursor = document.getElementById('agent-cursor');
    const visionBox = document.getElementById('vision-box');
    
    let i = 0;
    
    function typeWriter() {
        if (i < textToType.length) {
            typewriterElement.innerHTML += textToType.charAt(i);
            i++;
            setTimeout(typeWriter, 50 + Math.random() * 50);
        } else {
            // After typing, start the "agent execution" animation
            setTimeout(animateAgent, 1000);
        }
    }

    // Start typing after a short delay
    setTimeout(typeWriter, 1500);

    function animateAgent() {
        // Move mouse
        agentCursor.style.top = "30%";
        agentCursor.style.left = "40%";
        
        setTimeout(() => {
            // Show vision box (simulate parsing)
            visionBox.style.opacity = "1";
            visionBox.style.top = "25%";
            visionBox.style.left = "35%";
            visionBox.style.width = "200px";
            visionBox.style.height = "60px";
            
            setTimeout(() => {
                // Hide vision box, click and move
                visionBox.style.opacity = "0";
                agentCursor.style.transform = "scale(0.8)"; // simulate click
                
                setTimeout(() => {
                    agentCursor.style.transform = "scale(1)";
                    agentCursor.style.top = "60%";
                    agentCursor.style.left = "60%";
                }, 200);
                
            }, 1000);
            
        }, 1000);
    }
    
    // Looping animation
    setInterval(() => {
        i = 0;
        typewriterElement.innerHTML = '';
        agentCursor.style.top = "50%";
        agentCursor.style.left = "50%";
        visionBox.style.opacity = "0";
        setTimeout(typeWriter, 1000);
    }, 8000);
});
