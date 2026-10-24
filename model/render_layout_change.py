"""Compare actual STL sections for the requested latch shift and base extension."""
import sys,json
from pathlib import Path
from render_rounding import load,draw,side,ROOT
import matplotlib.pyplot as plt


def render(previous):
    old=load(previous);current=load(ROOT/'stl/760867899_clip.stl')
    settings=json.loads((ROOT/'model/parameters.json').read_text())
    fig,axes=plt.subplots(1,2,figsize=(12,7),facecolor='white')
    draw(axes[0],current.slice(1.25),'#b9d1df','#234a63')
    draw(axes[0],current.slice(1.25)-old.slice(1.25),'#9bc9b0','#28734d')
    draw(axes[0],old.slice(1.25),'none','#c46a2e')
    axes[0].set_xlim(-2,37);axes[0].set_ylim(-15,18)
    axes[0].set_title('Base plan · added 4 mm in green')
    axes[0].annotate('',xy=(30.3,15),xytext=(34.3,15),arrowprops={'arrowstyle':'<->','color':'#28734d'})
    axes[0].text(32.3,16,'+4 mm',ha='center',fontsize=11,color='#28734d')
    axes[0].set_xlabel('Length · X (mm)');axes[0].set_ylabel('Width · Y (mm)')
    draw(axes[1],side(current),'#b9d1df','#234a63',True)
    draw(axes[1],side(old),'none','#c46a2e',True)
    axes[1].set_xlim(-2,37);axes[1].set_ylim(-19,12)
    axes[1].set_title('Centre section · retaining clip moved +2 mm')
    axes[1].annotate('',xy=(29.3,8.5),xytext=(31.3,8.5),arrowprops={'arrowstyle':'<->','color':'#28734d'})
    axes[1].text(30.3,9.4,'+2 mm',ha='center',fontsize=11,color='#28734d')
    axes[1].set_xlabel('Length · X (mm)');axes[1].set_ylabel('Height · Z (mm)')
    for ax in axes:ax.set_aspect('equal');ax.grid(alpha=.15)
    fig.suptitle(settings['revision']+' · longer base and shifted retaining clip',fontsize=17)
    fig.text(.5,.03,'Blue: current STL · orange outline: v16 · peg, fins and hook stations retained',ha='center',fontsize=11,color='#555')
    fig.tight_layout(rect=(0,.07,1,.94));fig.savefig(ROOT/'previews/layout_change.png',dpi=170);plt.close(fig)


if __name__=='__main__':render(Path(sys.argv[1]))
