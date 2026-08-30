import { useState, type ReactNode } from "react";
import { motion, useDragControls, type PanInfo } from "framer-motion";

interface BottomSheetProps {
  onClose: () => void;
  children: ReactNode;
  header?: ReactNode;
  className?: string;
}

export const BottomSheet = ({
  onClose,
  children,
  header,
  className = "",
}: BottomSheetProps) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const dragControls = useDragControls();
  const isMobile = typeof window !== "undefined" && window.innerWidth < 768;
  const windowHeight = typeof window !== "undefined" ? window.innerHeight : 800;
  const variants = {
    mobile: {
      closed: { y: windowHeight },
      collapsed: { y: windowHeight * 0.4 },
      expanded: { y: 0 },
    },
    desktop: {
      closed: { x: "100%", y: 0 },
      open: { x: 0, y: 0 },
    },
  };

  const handleDragEnd = (
    _: MouseEvent | TouchEvent | PointerEvent,
    info: PanInfo,
  ) => {
    if (!isMobile) return;

    const velocity = info.velocity.y;
    const offset = info.offset.y;

    if (velocity < -300 || offset < -50) {
      setIsExpanded(true);
    } else if (velocity > 300 || offset > 50) {
      if (isExpanded) {
        setIsExpanded(false);
      } else {
        onClose();
      }
    }
  };

  return (
    <motion.div
      initial="closed"
      animate={isMobile ? (isExpanded ? "expanded" : "collapsed") : "open"}
      exit="closed"
      variants={isMobile ? variants.mobile : variants.desktop}
      transition={{ type: "spring", damping: 35, stiffness: 350, mass: 0.5 }}
      drag={isMobile ? "y" : false}
      dragControls={dragControls}
      dragConstraints={{ top: 0, bottom: windowHeight }}
      dragListener={false}
      dragElastic={0.2}
      onDragEnd={handleDragEnd}
      className={`absolute bottom-0 left-0 right-0 z-[60] bg-white rounded-t-3xl shadow-2xl
                  flex flex-col h-[100dvh]
                  md:h-full md:top-0 md:bottom-0 md:right-0 md:left-auto md:rounded-t-none md:rounded-l-3xl overflow-hidden ${className}`}
    >
      {isMobile && (
        <div
          onPointerDown={(e) => dragControls.start(e)}
          className="flex-shrink-0 w-full pt-4 pb-2 cursor-grab active:cursor-grabbing touch-none"
          style={{ touchAction: "none" }}
        >
          <div className="w-12 h-1.5 bg-gray-300 rounded-full mx-auto" />
        </div>
      )}

      <div
        onPointerDown={(e) => dragControls.start(e)}
        className="touch-none flex-shrink-0"
        style={{ touchAction: "none" }}
      >
        {header}
      </div>

      <div
        className="flex-1 overflow-y-auto p-5 space-y-8 touch-pan-y"
        style={{
          paddingBottom:
            isMobile && !isExpanded ? "calc(40dvh + 20px)" : "20px",
        }}
      >
        {children}
      </div>
    </motion.div>
  );
};
