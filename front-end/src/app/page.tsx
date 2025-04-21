'use client';
import { useEffect, useRef, useState } from 'react';
import Link from 'next/link';

/* ──────────────────────  PARAGRAPHS  ─────────────────────── */
const paragraphs: React.ReactNode[] = [
  <>
    The original&nbsp;
    <Link href="https://www.als.org/ibc" target="_blank" className="underline">
      Ice Bucket Challenge
    </Link>
    &nbsp;erupted in summer 2014 when ALS advocate Pete Frates and friends
    invited the internet to drench themselves in ice water, donate, and tag
    others—turning the social graph itself into a fundraiser.
  </>,
  <>
    In barely six weeks the movement generated 17 million uploads and delivered
    $115 million to the&nbsp;
    <Link href="https://www.als.org/ibc" target="_blank" className="underline">
      ALS Association
    </Link>
    , a windfall that seeded dozens of labs and even helped scientists identify
    the&nbsp;
    <Link
      href="https://time.com/4426072/ice-bucket-challenge-als-discovery/"
      target="_blank"
      className="underline"
    >
      NEK1 gene
    </Link>
    &nbsp;linked to ALS.
  </>,
  <>
    Teachers noticed students were obsessed with the meme, so&nbsp;
    <Link
      href="https://choices.scholastic.com/pages/content-hubs/decision-making/lesson-plan-are-you-following-the-herd.html"
      target="_blank"
      className="underline"
    >
      Scholastic Choices
    </Link>
    &nbsp;framed it in “herd‑mentality” lessons, letting English and health
    classes analyze peer influence while biology classes covered
    neuro‑degeneration.
  </>,
  <>
    A handful of risky copycats prompted schools to pair any challenge with
    adult supervision and clear safety norms, as seen in this&nbsp;
    <Link
      href="https://www.pbs.org/video/njtoday-mary-alice-williams-takes-icebucketchallenge/"
      target="_blank"
      className="underline"
    >
      2014 PBS clip
    </Link>
    .
  </>,
  <>
    Education writers on&nbsp;
    <Link
      href="https://www.edutopia.org/blog/empowering-student-changemakers-vicki-davis"
      target="_blank"
      className="underline"
    >
      Edutopia
    </Link>
    &nbsp;held it up as proof teens can become “social entrepreneurs” when armed
    with storytelling, empathy, and a clear call to action.
  </>,
  <>
    Mental‑health advocates soon wondered if the same formula could destigmatize
    anxiety and depression; by 2024&nbsp;
    <Link
      href="https://www.als.org/stories-news/new-report-highlights-progress-made-because-als-ice-bucket-challenge"
      target="_blank"
      className="underline"
    >
      retrospectives
    </Link>
    &nbsp;explicitly called the Challenge a blueprint for other causes.
  </>,
  <>
    In March 2025 the University of South Carolina’s&nbsp;
    <Link
      href="https://support.activeminds.org/fundraiser/6221101"
      target="_blank"
      className="underline"
    >
      MIND Club
    </Link>
    &nbsp;revived it as the “Speak Your MIND Ice Bucket Challenge,” asking
    participants to share a mental‑health tip and donate $5 to&nbsp;
    <Link
      href="https://www.activeminds.org/"
      target="_blank"
      className="underline"
    >
      Active Minds
    </Link>
    .
  </>,
  <>
    Regional outlets like&nbsp;
    <Link
      href="https://wset.com/news/local/a-bigger-deeper-meaning-new-ice-bucket-challenge-raises-awareness-for-mental-health-active-minds-non-profit-april-2025"
      target="_blank"
      className="underline"
    >
      WSET ABC‑13
    </Link>
    &nbsp;covered the relaunch, underscoring its “deeper meaning” for student
    wellness.
  </>,
  <>
    High‑schoolers joined fast: the student newspaper&nbsp;
    <Link
      href="https://sjcsabre.org/speak-your-mind-ice-bucket-challenge-raising-awareness-about-mental-health/"
      target="_blank"
      className="underline italic"
    >
      The Sabre
    </Link>
    &nbsp;documented teams nominating rivals between scrimmages to keep
    mental‑health talk front‑and‑center.
  </>,
  <>
    Many campuses slotted the challenge into spirit week; guidance counselors
    ran resource booths while science teachers explained cold‑shock physiology.
  </>,
  <>
    On TikTok the hashtag&nbsp;
    <Link
      href="https://www.tiktok.com/discover/how-to-play-the-usc-mind-ice-bucket-challenge"
      target="_blank"
      className="underline"
    >
      #SpeakYourMIND
    </Link>
    &nbsp;passed 200 million views in ten days, mirroring the 2014 viral curve.
  </>,
  <>
    Today advisers treat the reboot as both fundraiser and SEL lesson—pairing
    the public commitment with journaling prompts, peer‑support sign‑ups, and
    clear pathways to counseling.
  </>,
];

/* ──────────────────────  COMPONENT  ─────────────────────── */
export default function VideoScrollPage() {
  // New: Track mobile/desktop for opacity
  const [isMobile, setIsMobile] = useState(false);
  useEffect(() => {
    const checkMobile = () => setIsMobile(window.innerWidth < 768);
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  const videoRef  = useRef<HTMLVideoElement>(null);
  const scrollRef = useRef<HTMLDivElement>(null);
  const [fps,  setFps ] = useState(30);
  const [frame,setFrame]= useState(0);
  const [last, setLast ] = useState(0);


  const isDesktop = () => window.innerWidth >= 768;

  useEffect(() => {
    const video    = videoRef.current!;
    const scroller = scrollRef.current!;

    /* 1️⃣  make seeks work on iOS without letting it keep playing */
    const onMeta = async () => {
      if (video.duration && typeof (video as any).webkitDecodedFrameCount === 'number') {
        setFps(Math.round((video as any).webkitDecodedFrameCount / video.duration) || 30);
      }
      try {
        await video.play();   // buffer
        video.pause();        // freeze
      } catch {}
      video.currentTime = 0;
    };
    video.addEventListener('loadedmetadata', onMeta, { once:true });

    /* ensure any unexpected 'play' events are stopped */
    const stopLoop = () => video.pause();
    video.addEventListener('play', stopLoop);

    /* 2️⃣  scroll → seek */
    let ticking = false;
    const onScroll = () => {
      if (ticking) return;
      ticking = true;
      requestAnimationFrame(() => {
        const scrollPos = isDesktop() ? scroller.scrollTop : window.scrollY;
        const maxScroll = isDesktop()
          ? scroller.scrollHeight - scroller.clientHeight
          : document.body.scrollHeight - window.innerHeight;

        const progress = Math.min(scrollPos / maxScroll, 1);
        const target   = progress * video.duration;

        if (Math.abs(target - last) > 1 / fps) {
          video.currentTime = target;
          video.pause();               // <- keep it paused
          setLast(target);
          setFrame(Math.floor(target * fps));
        }
        ticking = false;
      });
    };

    const scrollTarget: any = isDesktop() ? scroller : window;
    scrollTarget.addEventListener('scroll', onScroll, { passive:true });

    return () => {
      scrollTarget.removeEventListener('scroll', onScroll);
      video.removeEventListener('play', stopLoop);
    };
  }, [fps, last]);

  /* ──────────────────────  UI  ─────────────────────── */
  return (
    <main className="relative flex flex-col md:flex-row w-full overflow-x-hidden">
      {/* 🎞 video */}
      <video
        ref={videoRef}
        src="/videos/slow-mo-3.mp4"
        muted playsInline preload="auto"
        className="
          fixed inset-0 -z-10 h-screen w-screen object-cover
          md:static md:w-1/2 md:h-screen
        "
      />

      {/* 📑 text */}
      <div
        ref={scrollRef}
        className="
          relative z-10 w-full flex flex-col items-center
          md:w-1/2 md:h-screen md:overflow-y-auto
        "
      >
        {paragraphs.map((node, i) => (
          <section
  key={i}
  className={`flex items-center justify-center w-full px-4${i < paragraphs.length - 1 ? ' mb-[100vh]' : ''}`}
>
            <article
  className={
    `${isMobile ? 'bg-black/50 backdrop-blur-none' : 'bg-black/70 backdrop-blur-sm'} text-white rounded-2xl shadow-lg p-8 max-w-2xl mx-auto break-words w-full`
  }
>
              <p className="text-lg leading-relaxed drop-shadow-lg m-0">{node}</p>
            </article>
          </section>
        ))}
      </div>

      {/* 🔢 frame readout */}
      <div className="fixed bottom-4 right-4 rounded bg-black/70 px-3 py-2 font-mono text-sm text-white">
        Frame&nbsp;{frame}
      </div>
    </main>
  );
}
