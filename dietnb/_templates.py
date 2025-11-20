"""
JavaScript templates for dietnb UI components.
"""

COPY_BUTTON_SCRIPT = """
<script>
(function() {
    function setupCopyBtn(btn) {
        btn.addEventListener('click', async (e) => {
            e.stopPropagation();
            const container = btn.closest('.dietnb-container');
            const img = container.querySelector('.dietnb-img');
            const src = img.currentSrc || img.src;
            
            const originalHTML = btn.innerHTML;
            btn.innerHTML = '⏳';
            btn.disabled = true;
            
            try {
                const response = await fetch(src);
                if (!response.ok) throw new Error('Failed to fetch image');
                const blob = await response.blob();
                
                await navigator.clipboard.write([
                    new ClipboardItem({ [blob.type]: blob })
                ]);
                
                btn.innerHTML = '✅';
                setTimeout(() => {
                    btn.innerHTML = originalHTML;
                    btn.disabled = false;
                }, 1500);
            } catch (err) {
                console.error('[dietnb] Copy failed:', err);
                btn.innerHTML = '❌';
                btn.title = 'Copy failed: ' + err.message;
                setTimeout(() => {
                    btn.innerHTML = originalHTML;
                    btn.disabled = false;
                    btn.title = '';
                }, 2500);
            }
        });
    }
    
    setTimeout(() => {
        const btns = document.querySelectorAll('.dietnb-copy-btn');
        btns.forEach(btn => {
            if (!btn.dataset.initialized) {
                setupCopyBtn(btn);
                btn.dataset.initialized = 'true';
            }
        });
    }, 50);
})();
</script>
"""

COPY_BUTTON_HTML = """
<div class="dietnb-container" style="position: relative; display: inline-block; max-width: 100%;">
    <img src="{img_src}" alt="{filename}" class="dietnb-img" style="max-width: 100%; height: auto;">
    <div style="position: absolute; top: 8px; right: 8px; z-index: 10; display: flex; gap: 4px;">
        <button class="dietnb-copy-btn" 
                style="background: rgba(255, 255, 255, 0.95); 
                       border: 1px solid rgba(0, 0, 0, 0.2);
                       border-radius: 4px; cursor: pointer; 
                       padding: 4px 8px; font-size: 13px;
                       box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                       transition: all 0.2s;
                       font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;"
                onmouseover="this.style.background='rgba(255,255,255,1)'; this.style.boxShadow='0 4px 8px rgba(0,0,0,0.15)';"
                onmouseout="this.style.background='rgba(255,255,255,0.95)'; this.style.boxShadow='0 2px 4px rgba(0,0,0,0.1)';">
            📋
        </button>
        <a href="{img_src}" download="{filename}"
           style="background: rgba(255, 255, 255, 0.95); 
                  border: 1px solid rgba(0, 0, 0, 0.2);
                  border-radius: 4px; cursor: pointer; 
                  padding: 4px 8px; font-size: 13px;
                  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                  transition: all 0.2s;
                  text-decoration: none;
                  display: inline-block;
                  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;"
           onmouseover="this.style.background='rgba(255,255,255,1)'; this.style.boxShadow='0 4px 8px rgba(0,0,0,0.15)';"
           onmouseout="this.style.background='rgba(255,255,255,0.95)'; this.style.boxShadow='0 2px 4px rgba(0,0,0,0.1)';"
           title="Download image">
            💾
        </a>
    </div>
</div>
"""
